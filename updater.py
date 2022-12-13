import json
import time

import web3

from configs import chain_configs, update_timeout, redis_prefix
from redis_client import redis_client
from multicallable import Multicallable

with open('abi.json') as fp:
    abi = json.load(fp)


def run_updator():
    for chain, config in chain_configs.items():
        address = config['main_contract']
        w3 = web3.Web3(web3.HTTPProvider(config['http_rpc']))
        config['main_contract'] = w3.eth.contract(address=address, abi=abi)
        if len(config['non_circulating_contracts']) > 0:
            config['chain_multicallable'] = Multicallable(address, abi, w3)

    while True:
        for chain, config in chain_configs.items():
            print('Checking ' + chain)
            try:
                total_supply = config['main_contract'].functions.totalSupply().call()
                if len(config['non_circulating_contracts']) > 0:
                    nc_balances = [a[0] for a in config['chain_multicallable'].balanceOf(
                        config['non_circulating_contracts'].values())]
                    total_supply -= sum(nc_balances)
                print(str(total_supply))
                redis_client.set(redis_prefix + chain, total_supply)
            except Exception as ex:
                print('Error:', ex)
        time.sleep(update_timeout)


if __name__ == '__main__':
    run_updator()
