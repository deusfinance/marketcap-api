import json
from collections import deque

import web3
from multicallable import Multicallable
from web3 import HTTPProvider

from constants import DEUS_ADDRESS, SPOOKY_USDC_FTM, SPOOKY_FTM_DEUS, PAIR_ABI, non_circulating_contracts, \
    XDEUS_DEUS_POOL, XDEUS_POOL_ABI, XDEUS_ADDRESS, xdeus_non_circulating_contracts
from config import rpcs

with open('abi.json') as fp:
    abi = json.load(fp)

w3 = web3.Web3(web3.HTTPProvider(rpcs['fantom'][0]))


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
    FDV = 'fdv'
    MARKETCAP = 'marketcap'
    PRICE = 'price'

    @classmethod
    def is_valid(cls, route):
        return route in (cls.CIRCULATING_SUPPLY, cls.TOTAL_SUPPLY, cls.FDV, cls.MARKETCAP, cls.PRICE)


def get_ftm_dex_price():
    ftm_fu_pair = w3.eth.contract(SPOOKY_USDC_FTM, abi=PAIR_ABI)
    usdc_reserve, ftm_reserve, _ = ftm_fu_pair.functions.getReserves().call()
    return usdc_reserve * 10 ** 12 / ftm_reserve


def deus_spooky():
    contract = w3.eth.contract(SPOOKY_FTM_DEUS, abi=PAIR_ABI)
    reserve_ftm, reserve_deus, _ = contract.functions.getReserves().call()
    return (reserve_ftm / reserve_deus) * get_ftm_dex_price()


def get_xdeus_ratio():
    pool_contract = w3.eth.contract(XDEUS_DEUS_POOL, abi=XDEUS_POOL_ABI)
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
        self.deus_contract = w3.eth.contract(DEUS_ADDRESS, abi=abi)
        self.xdeus_contract = w3.eth.contract(XDEUS_ADDRESS, abi=abi)
        if non_circulating_contracts.get(chain_name):
            self.mc = Multicallable(DEUS_ADDRESS, abi, w3)
        else:
            self.mc = None
        if xdeus_non_circulating_contracts.get(chain_name):
            self.xmc = Multicallable(XDEUS_ADDRESS, abi, w3)
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
        self.deus_contract = w3.eth.contract(DEUS_ADDRESS, abi=abi)
        self.xdeus_contract = w3.eth.contract(XDEUS_ADDRESS, abi=abi)
        if self.mc is not None:
            self.mc = Multicallable(DEUS_ADDRESS, abi, w3)
        if self.xmc is not None:
            self.xmc = Multicallable(XDEUS_ADDRESS, abi, w3)
