import time
from typing import Dict

from multicallable import Multicallable

from abi import ERC20_ABI
from settings import update_timeout, Network, XDEUS_ADDRESS, ARB_NO_SUPPLY
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
def deus_updater(managers: Dict[str, RPCManager]):
    print('***** DEUS *****')
    for chain in Network.deus_chains():
        mc = managers[chain].mc
        print(f'{chain:.^40}')
        try:
            excludes = set(managers[chain].network.excludes['deus'])
            nc_supply = sum(mc.balanceOf(excludes).call())
            supply = managers[chain].deus_contract.functions.totalSupply().call()
            if chain == Network.ARBITRUM:
                no_supply = sum(mc.balanceOf(ARB_NO_SUPPLY).call())
                print('ARB-NO-SUPPLY   :', no_supply / 1e18)
                supply -= no_supply
            marketcap_db.set(DataRedisKey.NC_SUPPLY + chain, nc_supply)
            marketcap_db.set(DataRedisKey.CHAIN_TOTAL_SUPPLY + chain, supply)
        except Exception as ex:
            print('Error:', ex)
            managers[chain].update_rpc()
        else:
            print('TOTAL-SUPPLY    :', supply / 1e18)
            print('NON-CIRCULATING :', nc_supply / 1e18)
            print('CIRCULATING-SUPP:', (supply - nc_supply) / 1e18)
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

    for chain in Network.xdeus_chains():
        xmc = Multicallable(XDEUS_ADDRESS, ERC20_ABI, managers[chain].w3)
        print(f'{chain:.^40}')
        try:
            excludes = set(managers[chain].network.excludes['xdeus'])
            nc_supply = sum(xmc.balanceOf(excludes).call())
            supply = xmc._target.functions.totalSupply().call()
            marketcap_db.set(DataRedisKey.X_NC_SUPPLY + chain, nc_supply)
            marketcap_db.set(DataRedisKey.X_CHAIN_TOTAL_SUPPLY + chain, supply)
        except Exception as ex:
            print('Error:', ex)
            managers[chain].update_rpc()
        else:
            print('TOTAL-SUPPLY    :', supply / 1e18)
            print('NON-CIRCULATING :', nc_supply / 1e18)
            print('CIRCULATING-SUPP:', (supply - nc_supply) / 1e18)
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
