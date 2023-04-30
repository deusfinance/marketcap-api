import re
from collections import deque, defaultdict
from typing import List, Dict

import requests
import web3
from multicallable import Multicallable
from web3 import HTTPProvider
from web3.contract import Contract

from abi import DEI_STRATEGY_ABI, ERC20_ABI, MASTERCHEF_XDEUS_ABI, PAIR_ABI, SWAP_FLASHLOAN_ABI, MASTERCHEF_HELPER_ABI
from constants import DEI_STRATEGY_ADDRESS, DEUS_ADDRESS, SPOOKY_USDC_FTM, SPOOKY_FTM_DEUS, XDEUS_DEUS_POOL, \
    XDEUS_ADDRESS, MASTERCHEF_XDEUS, SOLIDLY_XDEUS_DEUS, MASTERCHEF_HELPER, DEI_ADDRESS, SOLIDLY_WETH_DEUS, \
    SOLIDLY_WETH_DEI, SOLIDLY_USDC_DEI, dei_reserve_addresses, Network
from config import rpcs, sheet_url
from redis_client import price_db

w3 = web3.Web3(web3.HTTPProvider(rpcs['fantom'][0]))
masterchef_contract = w3.eth.contract(w3.toChecksumAddress(MASTERCHEF_XDEUS), abi=MASTERCHEF_XDEUS_ABI)
mc_helper = w3.eth.contract(MASTERCHEF_HELPER, abi=MASTERCHEF_HELPER_ABI)


class PriceRedisKey:
    xDEUS_RATIO = 'xDEUS_RATIO'  # decimals 6
    DEUS_SPOOKY = 'DEUS_SPOOKY'  # decimals 6
    DEUS_SPIRIT = 'DEUS_SPIRIT'  # decimals 6
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

    xDD_TL_FTM = 'xDD_TL_FTM'  # decimals 18
    xD_TL_FTM = 'xD_TL_FTM'  # decimals 18
    xDD_TL_ETH = 'xDD_TL_ETH'  # decimals 18

    TVL_SINGLE_XDEUS = 'TVL_SINGLE_XDEUS'
    TVL_XDEUS_DEUS = 'TVL_XDEUS_DEUS'
    TVL_LP_DEUS_FTM = 'TVL_LP_DEUS_FTM'
    TVL_LP_DEI_USDC = 'TVL_LP_DEI_USDC'
    TVL_BEETS_DEI_USDC = 'TVL_BEETS_DEI_USDC'
    TVL_SINGLE_BDEI = 'TVL_SINGLE_BDEI'
    TVL_DEI_BDEI = 'TVL_DEI_BDEI'
    TVL_SOLIDLY_XDEUS_DEUS = 'TVL_SOLIDLY_XDEUS_DEUS'
    TVL_SOLIDLY_WETH_DEUS = 'TVL_SOLIDLY_WETH_DEUS'
    TVL_SOLIDLY_WETH_DEI = 'TVL_SOLIDLY_WETH_DEI'
    TVL_SOLIDLY_USDC_DEI = 'TVL_SOLIDLY_USDC_DEI'

    RPS_XDEUS = 'RPS_MASTERCHEF_XDEUS'
    RPS_SPOOKY = 'RPS_MASTERCHEF_SPOOKY'
    RPS_BEETS = 'RPS_MASTERCHEF_BEETS'
    RPS_BDEI = 'RPS_MASTERCHEF_BDEI'

    AP_SINGLE_XDEUS = 'AP_SINGLE_XDEUS'
    AP_XDEUS_DEUS = 'AP_XDEUS_DEUS'
    AP_LP_DEUS_FTM = 'AP_LP_DEUS_FTM'
    AP_LP_DEI_USDC = 'AP_LP_DEI_USDC'
    AP_BEETS_DEI_USDC = 'AP_BEETS_DEI_USDC'
    AP_SINGLE_BDEI = 'AP_SINGLE_BDEI'
    AP_DEI_BDEI = 'AP_DEI_BDEI'

    DEUS_PER_WEEK = 'DEUS_PER_WEEK'
    DEI_CIRCULATING_SUPPLY = 'DEI_CIRCULATING_SUPPLY'
    DEI_RESERVES = 'DEI_RESERVES'
    DEI_JSON_RESERVES = 'DEI_JSON_RESERVES'
    DEI_SEIGNIORAGE_RATIO = 'DEI_SEIGNIORAGE_RATIO'
    DEI_TOTAL_SUPPLY = 'DEI_TOTAL_SUPPLY'


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

        w3 = self.get_w3()
        self.deus_contract = w3.eth.contract(DEUS_ADDRESS, abi=ERC20_ABI)
        self.xdeus_contract = w3.eth.contract(XDEUS_ADDRESS, abi=ERC20_ABI)
        self.dei_contract = w3.eth.contract(DEI_ADDRESS, abi=ERC20_ABI)
        self.usdc_contract = w3.eth.contract(self.network.usdc, abi=ERC20_ABI)

        if chain_name in Network.deus_chains():
            self.mc = Multicallable(DEUS_ADDRESS, ERC20_ABI, w3)
        else:
            self.mc = None
        if chain_name in Network.xdeus_chains():
            self.xmc = Multicallable(XDEUS_ADDRESS, ERC20_ABI, w3)
        else:
            self.xmc = None

    def get_w3(self):
        for rpc in self.rpcs:
            w3 = web3.Web3(HTTPProvider(rpc))
            if w3.isConnected():
                break
        return w3

    def update_rpc(self):
        w3 = self.get_w3()
        self.deus_contract = w3.eth.contract(DEUS_ADDRESS, abi=ERC20_ABI)
        self.xdeus_contract = w3.eth.contract(XDEUS_ADDRESS, abi=ERC20_ABI)
        self.dei_contract = w3.eth.contract(DEI_ADDRESS, abi=ERC20_ABI)
        self.usdc_contract = w3.eth.contract(self.network.usdc, abi=ERC20_ABI)
        if self.mc is not None:
            self.mc = Multicallable(DEUS_ADDRESS, ERC20_ABI, w3)
        if self.xmc is not None:
            self.xmc = Multicallable(XDEUS_ADDRESS, ERC20_ABI, w3)


def fetch_dei_reserves(managers: Dict[str, RPCManager]):
    reserves = defaultdict(lambda: defaultdict(list))
    total = 0
    token_balances = defaultdict(int)
    for network, accounts in dei_reserve_addresses.items():
        w3 = managers[network].get_w3()
        for account, tokens in accounts.items():
            for token in tokens:
                token_contract = w3.eth.contract(token, abi=ERC20_ABI)
                decimals = token_contract.functions.decimals().call()
                symbol = token_contract.functions.symbol().call()
                balance = token_contract.functions.balanceOf(account).call()
                amount = round(balance / 10 ** decimals, 2)
                reserves[account][network].append(dict(token=symbol, balance=str(amount)))
                token_balances[symbol] += amount
                total += amount
    return reserves, total, token_balances


def fetch_dei_total_supply(managers: Dict[str, RPCManager]):
    total_supply = 0
    for chain, manager in managers.items():
        pool = manager.network.dei_bridge_pool
        pool_balance = manager.dei_contract.functions.balanceOf(pool).call()
        total = manager.dei_contract.functions.totalSupply().call()
        total_supply += total - pool_balance
    return total_supply


def fetch_dei_seigniorage(manager: RPCManager):
    w3 = manager.get_w3()
    dei_strategy_contract = w3.eth.contract(DEI_STRATEGY_ADDRESS, abi=DEI_STRATEGY_ABI)
    mint_collateral_ratio = dei_strategy_contract.functions.mintCollateralRatio().call()
    redeem_collateral_ratio = dei_strategy_contract.functions.redeemCollateralRatio().call()
    dei_seigniorage = mint_collateral_ratio - redeem_collateral_ratio
    return dei_seigniorage


def fetch_deus_per_week():
    pattern = r'18</div></th><td class=\"s0\" dir=\"ltr\"></td><td class=\"s2\" dir=\"ltr\">([\d,.]+)<'
    response = requests.get(sheet_url)
    if response:
        raw_deus_per_week: str = re.findall(pattern, response.text)[0]
        deus_per_week = float(raw_deus_per_week.replace(',', ''))
        return deus_per_week


# get total lock
def get_tl(deus_ftm: Contract, deus_eth: Contract):
    tl_xdd_ftm = deus_ftm.functions.balanceOf(XDEUS_DEUS_POOL).call() * 2
    tl_xd_ftm = masterchef_contract.functions.totalDepositedAmount(0).call()
    tl_xdd_eth = deus_eth.functions.balanceOf(SOLIDLY_XDEUS_DEUS).call() * 2
    tl_xdd_ftm = round(tl_xdd_ftm / 1e18)
    tl_xd_ftm = round(tl_xd_ftm / 1e18)
    tl_xdd_eth = round(tl_xdd_eth / 1e18)
    return tl_xdd_ftm, tl_xd_ftm, tl_xdd_eth


def block_time(duration: int = 20_000):
    current_block = w3.eth.block_number
    b = w3.eth.get_block(current_block).timestamp
    a = w3.eth.get_block(current_block - duration).timestamp
    return (b - a) / duration


def get_reward_per_second():
    rps_xdeus, rps_spooky, rps_beets, tpb_bdei = mc_helper.functions.getRewardPerSecond().call()
    # rewardPerSecond = tokenPerBlock / blockTime
    rps_bdei = int(tpb_bdei / block_time())
    return rps_xdeus, rps_spooky, rps_beets, rps_bdei


def get_alloc_point():
    ap_xdeus0, ap_xdeus2, ap_spooky0, ap_spooky2, ap_beets, ap_bdei0, ap_bdei1 = mc_helper.functions.getAllocPoint().call()
    return ap_xdeus0, ap_xdeus2, ap_spooky0, ap_spooky2, ap_beets, ap_bdei0, ap_bdei1


def get_tvl(manager: RPCManager):
    tl_xdeus0, tl_xdeus2, tl_spooky0, tl_spooky2, tl_beets, tl_bdei0, tl_bdei1 = mc_helper.functions.getTVL().call()
    _deus_price = int(price_db.get(PriceRedisKey.DEUS_SPOOKY)) / 1e6
    _xdeus_ratio = int(price_db.get(PriceRedisKey.xDEUS_RATIO)) / 1e6
    _xdeus_price = _deus_price * _xdeus_ratio
    _legacy_dei_price = int(price_db.get(PriceRedisKey.legacyDEI_SPOOKY)) / 1e6
    tvl_xdeus0 = round(tl_xdeus0 * _xdeus_price / 1e18)
    tvl_xdeus2 = round(tl_xdeus2 * _xdeus_price / 1e18)
    tvl_spooky0 = round(tl_spooky0 * _deus_price / 1e18)
    tvl_spooky2 = round(tl_spooky2 / 1e18)
    tvl_beets = round(tl_beets / 1e18)
    tvl_bdei0 = round(tl_bdei0 * _legacy_dei_price / 1e18)
    tvl_bdei1 = round(tl_bdei1 * _legacy_dei_price / 1e18)
    tl_solidly0 = manager.deus_contract.functions.balanceOf(SOLIDLY_XDEUS_DEUS).call() * 2
    tl_solidly1 = manager.deus_contract.functions.balanceOf(SOLIDLY_WETH_DEUS).call() * 2
    tl_solidly2 = manager.dei_contract.functions.balanceOf(SOLIDLY_WETH_DEI).call() * 2
    _dei_balance = manager.dei_contract.functions.balanceOf(SOLIDLY_USDC_DEI).call()
    _usdc_balance = manager.usdc_contract.functions.balanceOf(SOLIDLY_USDC_DEI).call()
    tl_solidly3 = _dei_balance + _usdc_balance * 10 ** 12
    tvl_solidly0 = round(tl_solidly0 * _deus_price / 1e18)
    tvl_solidly1 = round(tl_solidly1 * _deus_price / 1e18)
    tvl_solidly2 = round(tl_solidly2 / 1e18)
    tvl_solidly3 = round(tl_solidly3 / 1e18)
    return (tvl_xdeus0, tvl_xdeus2, tvl_spooky0, tvl_spooky2, tvl_beets, tvl_bdei0, tvl_bdei1,
            tvl_solidly0, tvl_solidly1, tvl_solidly2, tvl_solidly3)


def fetch_dei_circulating_supply(manager: RPCManager):
    return manager.dei_contract.functions.totalSupply().call()


def get_xdeus_reward(xdeus_contract):
    tda = masterchef_contract.functions.totalDepositedAmount(0).call()
    reward = xdeus_contract.functions.balanceOf(MASTERCHEF_XDEUS).call() - tda
    return max(reward, 0)


def get_ftm_dex_price():
    ftm_fu_pair = w3.eth.contract(SPOOKY_USDC_FTM, abi=PAIR_ABI)
    usdc_reserve, ftm_reserve, _ = ftm_fu_pair.functions.getReserves().call()
    return usdc_reserve * 10 ** 12 / ftm_reserve


def deus_spooky():
    contract = w3.eth.contract(SPOOKY_FTM_DEUS, abi=PAIR_ABI)
    reserve_ftm, reserve_deus, _ = contract.functions.getReserves().call()
    return (reserve_ftm / reserve_deus) * get_ftm_dex_price()


def get_xdeus_ratio():
    pool_contract = w3.eth.contract(XDEUS_DEUS_POOL, abi=SWAP_FLASHLOAN_ABI)
    dx = 1_000_000
    amount = pool_contract.functions.calculateSwap(0, 1, dx).call()
    return round(amount / dx, 3)


def xdeus_price():
    return get_xdeus_ratio() * deus_spooky()
