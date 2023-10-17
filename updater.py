import time
from typing import Dict

from config import update_timeout
from constants import veDEUS_ADDRESS, Network
from redis_client import marketcap_db

from utils import RPCManager, deus_chronos, xdeus_price, get_xdeus_reward, DataRedisKey, get_reward_per_second, \
    fetch_deus_per_week


def handle_error(func):
    def new_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            raise
        except Exception as ex:
            print(f'Error on `{func.__name__}`:', ex)

    new_func.__name__ = func.__name__
    return new_func


@handle_error
def deus_updater(managers):
    print('***** DEUS *****')
    for chain in Network.deus_chains():
        deus_contract = managers[chain].deus_contract
        mc = managers[chain].mc
        bridge_pool = managers[chain].network.dues_bridge_pool
        nc_contracts = managers[chain].network.deus_non_circulating
        print(f'{chain:.^40}')
        try:
            if bridge_pool:
                pool_supply = deus_contract.functions.balanceOf(bridge_pool).call()
            else:
                pool_supply = 0
            ve_deus = deus_contract.functions.balanceOf(veDEUS_ADDRESS).call() if chain == Network.FANTOM else 0
            chain_total_supply = deus_contract.functions.totalSupply().call()
            total_supply = chain_total_supply - pool_supply - ve_deus
            if nc_contracts:
                nc_supply = sum(balance[0] for balance in mc.balanceOf(set(nc_contracts.values())))
            else:
                nc_supply = 0
            marketcap_db.set(DataRedisKey.CHAIN_TOTAL_SUPPLY + chain, chain_total_supply)
            marketcap_db.set(DataRedisKey.SUPPLY_IN_BRIDGE_CONTRACTS + chain, pool_supply)
            marketcap_db.set(DataRedisKey.SUPPLY_IN_VEDEUS_CONTRACT + chain, ve_deus)
            marketcap_db.set(DataRedisKey.NC_SUPPLY + chain, nc_supply)
            marketcap_db.set(DataRedisKey.TOTAL_SUPPLY + chain, total_supply)
        except Exception as ex:
            print('Error:', ex)
            managers[chain].update_rpc()
        else:
            print('TOTAL SUPPLY:   ', total_supply)
            print('NON-CIRCULATING:', nc_supply)
            print('CIRCULATING:', total_supply - nc_supply)
    try:
        price = str(deus_chronos())
        marketcap_db.set(DataRedisKey.PRICE_TAG, price)
    except Exception as ex:
        print('Error:', ex)
    else:
        print(f'\n*** DEUS PRICE ***\n{price}\n')


@handle_error
def xdeus_updater(managers: Dict[str, RPCManager]):
    print('***** xDEUS *****')

    chain = Network.FANTOM
    xdeus_contract = managers[chain].xdeus_contract
    print(f'{chain:.^40}')
    try:
        pool_supply = xdeus_contract.functions.balanceOf(managers[chain].network.xdeus_bridge_pool).call()
        msig_supply = xdeus_contract.functions.balanceOf(
            managers[chain].network.xdeus_non_circulating['DEUS mSig']).call()
        print('msig balance:', msig_supply)
        reward = get_xdeus_reward(xdeus_contract)
        print('Reward:', reward)
        nc_supply = msig_supply + reward
        chain_total_supply = xdeus_contract.functions.totalSupply().call()
        supply = chain_total_supply
        circulating_supply = supply - nc_supply
        marketcap_db.set(DataRedisKey.X_NC_SUPPLY + chain, nc_supply)
        marketcap_db.set(DataRedisKey.X_TOTAL_SUPPLY + chain, supply)
        marketcap_db.set(DataRedisKey.X_CHAIN_TOTAL_SUPPLY + chain, chain_total_supply)
        marketcap_db.set(DataRedisKey.X_SUPPLY_IN_BRIDGE_CONTRACTS + chain, pool_supply)
    except Exception as ex:
        print('Error:', ex)
        managers[chain].update_rpc()
    else:
        print('CHAIN TOTAL SUPPLY: ', chain_total_supply)
        print('TOTAL SUPPLY:   ', supply)
        print('NON-CIRCULATING:', nc_supply)
        print('CIRCULATING:', circulating_supply)
    try:
        price = str(xdeus_price())
        marketcap_db.set(DataRedisKey.X_PRICE_TAG, price)
    except Exception as ex:
        print('Error:', ex)
    else:
        print(f'\n*** xDEUS PRICE ***\n{price}\n')


@handle_error
def reward_per_second_updater():
    keys = [DataRedisKey.RPS_XDEUS,
            DataRedisKey.RPS_SPOOKY,
            DataRedisKey.RPS_BEETS,
            DataRedisKey.RPS_BDEI]
    all_rps = get_reward_per_second()
    for key, rps in zip(keys, all_rps):
        print(f'{key}:\t{rps}')
        marketcap_db.set(key, rps)


@handle_error
def deus_per_week_updater():
    deus_per_week = fetch_deus_per_week()
    if deus_per_week:
        print('DeusPerWeek:', deus_per_week)
        marketcap_db.set(DataRedisKey.DEUS_PER_WEEK, deus_per_week)


def run_updater():
    deus_managers = {chain: RPCManager(chain) for chain in Network.deus_chains()}
    while True:
        slow = 0
        try:
            deus_updater(deus_managers)
            xdeus_updater(deus_managers)
            reward_per_second_updater()
            if slow > 0:
                slow -= 1
            else:
                deus_per_week_updater()
                slow = 60
        except KeyboardInterrupt:
            break
        time.sleep(update_timeout)


if __name__ == '__main__':
    run_updater()
