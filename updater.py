import json
import time
from typing import Dict

from config import update_timeout
from constants import veDEUS_ADDRESS, Network
from redis_client import marketcap_db

from utils import RPCManager, deus_spooky, xdeus_price, get_xdeus_reward, get_tl, DataRedisKey, get_tvl, \
    get_alloc_point, get_reward_per_second, fetch_deus_per_week, fetch_dei_circulating_supply, fetch_dei_reserves, \
    fetch_dei_seigniorage, fetch_dei_total_supply, fetch_protocol_owned_dei


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
def dei_updater(managers):
    print('***** DEI *****')
    circulating_supply = fetch_dei_circulating_supply(managers['fantom'])
    print('Circ Supply:', circulating_supply // 10 ** 18)
    marketcap_db.set(DataRedisKey.DEI_CIRCULATING_SUPPLY, circulating_supply)
    dei_seigniorage_ratio = fetch_dei_seigniorage(managers['fantom'])
    print('DEI Seigniorage ratio:', dei_seigniorage_ratio)
    marketcap_db.set(DataRedisKey.DEI_SEIGNIORAGE_RATIO, dei_seigniorage_ratio)


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
        price = str(deus_spooky())
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
def tl_updater(managers):
    print('***** Total Lock *****')
    tl_xdd_ftm, tl_xd_ftm, tl_xdd_eth = get_tl(managers['fantom'].deus_contract, managers['mainnet'].deus_contract)
    print('TL xDEUS/DEUS ftm:', tl_xdd_ftm)
    print('TL xDEUS ftm:     ', tl_xd_ftm)
    print('TL xDEUS/DEUS eth:', tl_xdd_eth)
    marketcap_db.set(DataRedisKey.xDD_TL_FTM, tl_xdd_ftm)
    marketcap_db.set(DataRedisKey.xD_TL_FTM, tl_xd_ftm)
    marketcap_db.set(DataRedisKey.xDD_TL_ETH, tl_xdd_eth)


@handle_error
def tvl_updater(managers):
    keys = [DataRedisKey.TVL_SINGLE_XDEUS,
            DataRedisKey.TVL_XDEUS_DEUS,
            DataRedisKey.TVL_LP_DEUS_FTM,
            DataRedisKey.TVL_LP_DEI_USDC,
            DataRedisKey.TVL_BEETS_DEI_USDC,
            DataRedisKey.TVL_SINGLE_BDEI,
            DataRedisKey.TVL_DEI_BDEI,
            DataRedisKey.TVL_SOLIDLY_XDEUS_DEUS,
            DataRedisKey.TVL_SOLIDLY_WETH_DEUS,
            DataRedisKey.TVL_SOLIDLY_WETH_DEI,
            DataRedisKey.TVL_SOLIDLY_USDC_DEI]
    all_tvl = get_tvl(managers['mainnet'])
    for key, tvl in zip(keys, all_tvl):
        print(f'{key}:\t${tvl:,}')
        marketcap_db.set(key, tvl)


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
def alloc_point_updater():
    keys = [DataRedisKey.AP_SINGLE_XDEUS,
            DataRedisKey.AP_XDEUS_DEUS,
            DataRedisKey.AP_LP_DEUS_FTM,
            DataRedisKey.AP_LP_DEI_USDC,
            DataRedisKey.AP_BEETS_DEI_USDC,
            DataRedisKey.AP_SINGLE_BDEI,
            DataRedisKey.AP_DEI_BDEI]
    all_ap = get_alloc_point()
    for key, ap in zip(keys, all_ap):
        print(f'{key}:\t{ap}')
        marketcap_db.set(key, ap)


@handle_error
def deus_per_week_updater():
    deus_per_week = fetch_deus_per_week()
    if deus_per_week:
        print('DeusPerWeek:', deus_per_week)
        marketcap_db.set(DataRedisKey.DEUS_PER_WEEK, deus_per_week)


@handle_error
def dei_reserves_updater(managers):
    reserves, total, token_balances = fetch_dei_reserves(managers)
    print(f'DEI reserves: {total:,.2f}')
    marketcap_db.set(DataRedisKey.DEI_RESERVES, round(total))
    marketcap_db.set(DataRedisKey.DEI_JSON_RESERVES,
                     json.dumps({'wallets': reserves,
                                 'tokenBalances': token_balances,
                                 'total': str(round(total))}))


@handle_error
def dei_total_supply_updater(managers):
    total_supply = fetch_dei_total_supply(managers)
    print(f'DEI total supply: {total_supply / 1e18:,.2f}')
    marketcap_db.set(DataRedisKey.DEI_TOTAL_SUPPLY, total_supply)


@handle_error
def protocol_owned_dei_updater(managers):
    owned_dei = fetch_protocol_owned_dei(managers)
    print(f'Protocol owned DEI: {owned_dei / 1e18:,.2f}')
    marketcap_db.set(DataRedisKey.PROTOCOL_OWNED_DEI, owned_dei)


def run_updater():
    deus_managers = {chain: RPCManager(chain) for chain in Network.deus_chains()}
    dei_managers = {chain: RPCManager(chain) for chain in Network.dei_chains()}
    while True:
        slow = 0
        try:
            deus_updater(deus_managers)
            xdeus_updater(deus_managers)
            dei_updater(dei_managers)
            tl_updater(deus_managers)
            tvl_updater(deus_managers)
            reward_per_second_updater()
            alloc_point_updater()
            dei_reserves_updater(deus_managers)
            dei_total_supply_updater(dei_managers)
            protocol_owned_dei_updater(dei_managers)
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
