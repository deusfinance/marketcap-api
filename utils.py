import json
from collections import deque

import web3
from multicallable import Multicallable
from web3 import HTTPProvider

from constants import DEUS_ADDRESS, SPOOKY_USDC_FTM, SPOOKY_FTM_DEUS, PAIR_ABI
from config import rpcs

with open('abi.json') as fp:
    abi = json.load(fp)

w3 = web3.Web3(web3.HTTPProvider(rpcs['fantom'][0]))


def get_ftm_dex_price():
    ftm_fu_pair = w3.eth.contract(SPOOKY_USDC_FTM, abi=PAIR_ABI)
    usdc_reserve, ftm_reserve, _ = ftm_fu_pair.functions.getReserves().call()
    return usdc_reserve * 10 ** 12 / ftm_reserve


def deus_spooky():
    contract = w3.eth.contract(SPOOKY_FTM_DEUS, abi=PAIR_ABI)
    reserve_ftm, reserve_deus, _ = contract.functions.getReserves().call()
    return (reserve_ftm / reserve_deus) * get_ftm_dex_price()


class RPCManager:
    def __init__(self, chain_name: str):
        self.chain_name = chain_name
        self.rpcs = deque(rpcs[chain_name])

        w3 = self.get_w3()
        self.deus_contract = w3.eth.contract(DEUS_ADDRESS, abi=abi)
        self.mc = Multicallable(DEUS_ADDRESS, abi, w3)

    def get_w3(self):
        for rpc in self.rpcs:
            w3 = web3.Web3(HTTPProvider(rpc))
            if w3.isConnected():
                break
        return w3

    def update_rpc(self):
        w3 = self.get_w3()
        self.deus_contract = w3.eth.contract(DEUS_ADDRESS, abi=abi)
        self.mc = Multicallable(DEUS_ADDRESS, abi, w3)
