import time

from config import update_timeout, NC_SUPPLY_REDIS_PREFIX, PRICE_REDIS_TAG, TOTAL_SUPPLY_REDIS_PREFIX
from constants import non_circulating_contracts, bridge_pools
from redis_client import redis_client

from utils import RPCManager, deus_spooky


def run_updator():
    managers = {}
    for chain, _ in non_circulating_contracts.items():
        managers[chain] = RPCManager(chain)

    while True:
        for chain, contracts in non_circulating_contracts.items():
            deus_contract = managers[chain].deus_contract
            mc = managers[chain].mc
            print(f'{chain:.^40}')
            try:
                if chain in bridge_pools:
                    pool_supply = deus_contract.functions.balanceOf(bridge_pools[chain]).call()
                else:
                    pool_supply = 0
                total_supply = deus_contract.functions.totalSupply().call() - pool_supply
                if contracts:
                    nc_supply = sum(balance[0] for balance in mc.balanceOf(set(contracts.values())))
                else:
                    nc_supply = 0
                redis_client.set(NC_SUPPLY_REDIS_PREFIX + chain, nc_supply)
                redis_client.set(TOTAL_SUPPLY_REDIS_PREFIX + chain, total_supply)
            except Exception as ex:
                print('Error:', ex)
                managers[chain].update_rpc()
            else:
                print('TOTAL SUPPLY:   ', total_supply)
                print('NON-CIRCULATING:', nc_supply)
        try:
            price = str(deus_spooky())
            redis_client.set(PRICE_REDIS_TAG, price)
        except Exception as ex:
            print('Error:', ex)
        else:
            print(f'\n*** DEUS PRICE ***\n{price}\n')

        time.sleep(update_timeout)


if __name__ == '__main__':
    run_updator()
