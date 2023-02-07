import json
from collections import deque

import web3
from multicallable import Multicallable
from web3 import HTTPProvider
from web3.contract import Contract

from abi import ERC20_ABI, MASTERCHEF_XDEUS_ABI, PAIR_ABI, SWAP_FLASHLOAN_ABI
from constants import DEUS_ADDRESS, SPOOKY_USDC_FTM, SPOOKY_FTM_DEUS, non_circulating_contracts, XDEUS_DEUS_POOL, \
    XDEUS_ADDRESS, xdeus_non_circulating_contracts, MASTERCHEF_XDEUS, XDEUS_DEUS_SOLIDLY
from config import rpcs

w3 = web3.Web3(web3.HTTPProvider(rpcs['fantom'][0]))
masterchef_contract = w3.eth.contract(w3.toChecksumAddress(MASTERCHEF_XDEUS), abi=MASTERCHEF_XDEUS_ABI)


class RedisKey:
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


class RouteName:
    CIRCULATING_SUPPLY = 'circulating-supply'
    TOTAL_SUPPLY = 'total-supply'
    NON_CIRCULATING_SUPPLY = 'non-circulating-supply'
    FDV = 'fdv'
    MARKETCAP = 'marketcap'
    PRICE = 'price'

    @classmethod
    def is_valid(cls, route):
        return route in (cls.CIRCULATING_SUPPLY, cls.NON_CIRCULATING_SUPPLY, cls.TOTAL_SUPPLY, cls.FDV, cls.MARKETCAP, cls.PRICE)


# get total lock
def get_tl(deus_ftm: Contract, deus_eth: Contract):
    tl_xdd_ftm = deus_ftm.functions.balanceOf(XDEUS_DEUS_POOL).call() * 2
    tl_xd_ftm = masterchef_contract.functions.totalDepositedAmount(0).call()
    tl_xdd_eth = deus_eth.functions.balanceOf(XDEUS_DEUS_SOLIDLY).call() * 2
    tl_xdd_ftm = round(tl_xdd_ftm / 1e18)
    tl_xd_ftm = round(tl_xd_ftm / 1e18)
    tl_xdd_eth = round(tl_xdd_eth / 1e18)
    return tl_xdd_ftm, tl_xd_ftm, tl_xdd_eth


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


class RPCManager:
    def __init__(self, chain_name: str):
        self.chain_name = chain_name
        self.rpcs = deque(rpcs[chain_name])

        w3 = self.get_w3()
        self.deus_contract = w3.eth.contract(DEUS_ADDRESS, abi=ERC20_ABI)
        self.xdeus_contract = w3.eth.contract(XDEUS_ADDRESS, abi=ERC20_ABI)
        if non_circulating_contracts.get(chain_name):
            self.mc = Multicallable(DEUS_ADDRESS, ERC20_ABI, w3)
        else:
            self.mc = None
        if xdeus_non_circulating_contracts.get(chain_name):
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
        if self.mc is not None:
            self.mc = Multicallable(DEUS_ADDRESS, ERC20_ABI, w3)
        if self.xmc is not None:
            self.xmc = Multicallable(XDEUS_ADDRESS, ERC20_ABI, w3)
