import re
from collections import deque
import requests
import web3
from multicallable import Multicallable
from web3 import HTTPProvider

from abi import ERC20_ABI, MASTERCHEF_XDEUS_ABI, SWAP_FLASHLOAN_ABI, MASTERCHEF_HELPER_ABI
from settings import DEUS_ADDRESS, XDEUS_DEUS_POOL, MASTERCHEF_XDEUS, MASTERCHEF_HELPER, Network, rpcs, sheet_url, \
    symm_api_url
from redis_client import price_db

ftm_w3 = web3.Web3(web3.HTTPProvider(rpcs['fantom'][0]))
masterchef_contract = ftm_w3.eth.contract(ftm_w3.to_checksum_address(MASTERCHEF_XDEUS), abi=MASTERCHEF_XDEUS_ABI)
mc_helper = ftm_w3.eth.contract(MASTERCHEF_HELPER, abi=MASTERCHEF_HELPER_ABI)


class PriceRedisKey:
    xDEUS_RATIO = 'xDEUS_RATIO'  # decimals 6
    DEUS_SPOOKY = 'DEUS_SPOOKYSWAP'  # decimals 6
    DEUS_SPIRIT = 'DEUS_SPIRITSWAP'  # decimals 6
    legacyDEI_SPOOKY = 'legacyDEI_SPOOKY'  # decimals 6
    legacyDEI_SPIRIT = 'legacyDEI_SPIRIT'  # decimals 6
    legacyDEI_SOLIDLY = 'legacyDEI_SOLIDLY'  # decimals 6
    legacyDEI_BEETS = 'legacyDEI_BEETS'  # decimals 6
    DEI_FIREBIRD = 'DEI_FIREBIRD'  # decimals 6
    DEUS_GATEIO = 'DEUS_GATEIO'  # float
    DEUS_MEXC = 'DEUS_MEXC'  # float
    DEUS_SOLIDLY_ETH = 'DEUS_SOLIDLY_ETH'  # decimals 6
    DEI_SOLIDLY_ETH = 'DEI_SOLIDLY_ETH'  # decimals 6
    USDC_KRAKEN = 'USDC_KRAKEN'  # float
    DEUS_CHRONOS = 'DEUS_CHRONOS'  # decimals 6


class DataRedisKey:
    CHAIN_TOTAL_SUPPLY = 'CHAIN_TOTAL_SUPPLY_'
    SUPPLY_IN_BRIDGE_CONTRACTS = 'SUPPLY_IN_BRIDGE_CONTRACTS_'
    SUPPLY_IN_VEDEUS_CONTRACT = 'SUPPLY_IN_VEDEUS_CONTRACT_'
    NC_SUPPLY = 'NON_CIRCULATING_SUPPLY_'
    TOTAL_SUPPLY = 'TOTAL_SUPPLY_'
    X_NC_SUPPLY = 'X_NON_CIRCULATING_SUPPLY_'
    X_CHAIN_TOTAL_SUPPLY = 'X_CHAIN_TOTAL_SUPPLY_'
    X_TOTAL_SUPPLY = 'X_TOTAL_SUPPLY_'
    X_SUPPLY_IN_BRIDGE_CONTRACTS = 'X_SUPPLY_IN_BRIDGE_CONTRACTS_'

    PRICE_TAG = 'DEUS_PRICE'
    X_PRICE_TAG = 'XDEUS_PRICE'

    RPS_XDEUS = 'RPS_MASTERCHEF_XDEUS'
    RPS_SPOOKY = 'RPS_MASTERCHEF_SPOOKY'
    RPS_BEETS = 'RPS_MASTERCHEF_BEETS'
    RPS_BDEI = 'RPS_MASTERCHEF_BDEI'

    DEUS_PER_WEEK = 'DEUS_PER_WEEK'


class RouteName:
    CIRCULATING_SUPPLY = 'circulating-supply'
    TOTAL_SUPPLY = 'total-supply'
    NON_CIRCULATING_SUPPLY = 'non-circulating-supply'
    FDV = 'fdv'
    MARKETCAP = 'marketcap'
    PRICE = 'price'

    @classmethod
    def is_valid(cls, route):
        return route in (
            cls.CIRCULATING_SUPPLY, cls.NON_CIRCULATING_SUPPLY, cls.TOTAL_SUPPLY, cls.FDV, cls.MARKETCAP, cls.PRICE)


class RPCManager:
    def __init__(self, chain_name: str):
        self.chain_name = chain_name
        self.rpcs = deque(rpcs[chain_name])
        self.network = Network(chain_name)

        self.w3 = self.get_w3()
        self.deus_contract = self.w3.eth.contract(DEUS_ADDRESS, abi=ERC20_ABI)
        self.mc = Multicallable(DEUS_ADDRESS, ERC20_ABI, self.w3)

    def get_w3(self):
        for rpc in self.rpcs:
            w3 = web3.Web3(HTTPProvider(rpc))
            if w3.is_connected():
                return w3
        raise Exception(f'no RPC connected for {self.chain_name}')

    def update_rpc(self):
        self.w3 = self.get_w3()
        self.deus_contract = self.w3.eth.contract(DEUS_ADDRESS, abi=ERC20_ABI)
        self.mc = Multicallable(DEUS_ADDRESS, ERC20_ABI, self.w3)


def fetch_deus_per_week():
    return '913.58'
    # pattern = r'18</div></th><td class=\"s0\" dir=\"ltr\"></td><td class=\"s2\" dir=\"ltr\">([\d,.]+)<'
    # response = requests.get(sheet_url)
    # if response:
    #     raw_deus_per_week: str = re.findall(pattern, response.text)[0]
    #     deus_per_week = float(raw_deus_per_week.replace(',', ''))
    #     return deus_per_week


def block_time(duration: int = 20_000):
    current_block = ftm_w3.eth.block_number
    b = ftm_w3.eth.get_block(current_block).timestamp
    a = ftm_w3.eth.get_block(current_block - duration).timestamp
    return (b - a) / duration


def get_reward_per_second():
    rps_xdeus, rps_spooky, rps_beets, tpb_bdei = mc_helper.functions.getRewardPerSecond().call()
    # rewardPerSecond = tokenPerBlock / blockTime
    rps_bdei = int(tpb_bdei / block_time())
    return rps_xdeus, rps_spooky, rps_beets, rps_bdei


def get_xdeus_reward(xdeus_contract):
    tda = masterchef_contract.functions.totalDepositedAmount(0).call()
    reward = xdeus_contract.functions.balanceOf(MASTERCHEF_XDEUS).call() - tda
    return max(reward, 0)


def deus_chronos():
    return int(price_db.get(PriceRedisKey.DEUS_CHRONOS)) / 1e6


def get_xdeus_ratio():
    pool_contract = ftm_w3.eth.contract(XDEUS_DEUS_POOL, abi=SWAP_FLASHLOAN_ABI)
    dx = 1_000_000
    amount = pool_contract.functions.calculateSwap(0, 1, dx).call()
    return round(amount / dx, 3)


def xdeus_price():
    return get_xdeus_ratio() * deus_chronos()


def get_deus_remaining():
    url = f'{symm_api_url}/v1/info'
    response = requests.get(url)
    if response:
        info = response.json()
        return round(float(info['total_migrated_to_deus']))
    return None
