import time

from config import update_timeout
from constants import non_circulating_contracts, bridge_pools, xdeus_non_circulating_contracts, xdeus_bridge_pools, \
    veDEUS_ADDRESS
from redis_client import marketcap_db

from utils import RPCManager, deus_spooky, xdeus_price, get_xdeus_reward, get_tl, DataRedisKey, get_tvl, \
    get_alloc_point, get_reward_per_second


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
def deus_updator(managers):
    print('***** DEUS *****')
    for chain, contracts in non_circulating_contracts.items():
        deus_contract = managers[chain].deus_contract
        mc = managers[chain].mc
        print(f'{chain:.^40}')
        try:
            if chain in bridge_pools:
                pool_supply = deus_contract.functions.balanceOf(bridge_pools[chain]).call()
            else:
                pool_supply = 0
            ve_deus = deus_contract.functions.balanceOf(veDEUS_ADDRESS).call() if chain == 'fantom' else 0
            chain_total_supply = deus_contract.functions.totalSupply().call()
            total_supply = chain_total_supply - pool_supply - ve_deus
            if contracts:
                nc_supply = sum(balance[0] for balance in mc.balanceOf(set(contracts.values())))
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
def xdeus_updator(managers):
    print('***** xDEUS *****')
    for chain, contracts in xdeus_non_circulating_contracts.items():
        xdeus_contract = managers[chain].xdeus_contract
        xmc = managers[chain].xmc
        print(f'{chain:.^40}')
        try:
            if chain in xdeus_bridge_pools:
                pool_supply = xdeus_contract.functions.balanceOf(xdeus_bridge_pools[chain]).call()
            else:
                pool_supply = 0
            msig_supply = xdeus_contract.functions.balanceOf(contracts['DEUS mSig']).call() if chain == 'fantom' else 0
            print('msig balance:', msig_supply)
            reward = get_xdeus_reward(xdeus_contract)
            print('Reward:', reward)
            nc_supply = msig_supply + reward
            chain_total_supply = xdeus_contract.functions.totalSupply().call()
            supply = chain_total_supply
            circulating_supply = supply - nc_supply
            # if contracts:
            #     nc_supply = sum(balance[0] for balance in xmc.balanceOf(set(contracts.values())))
            # else:
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
def tl_updator(managers):
    print('***** Total Lock *****')
    tl_xdd_ftm, tl_xd_ftm, tl_xdd_eth = get_tl(managers['fantom'].deus_contract, managers['mainnet'].deus_contract)
    print('TL xDEUS/DEUS ftm:', tl_xdd_ftm)
    print('TL xDEUS ftm:     ', tl_xd_ftm)
    print('TL xDEUS/DEUS eth:', tl_xdd_eth)
    marketcap_db.set(DataRedisKey.xDD_TL_FTM, tl_xdd_ftm)
    marketcap_db.set(DataRedisKey.xD_TL_FTM, tl_xd_ftm)
    marketcap_db.set(DataRedisKey.xDD_TL_ETH, tl_xdd_eth)


@handle_error
def tvl_updator(managers):
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
def reward_per_second_updator():
    keys = [DataRedisKey.RPS_XDEUS,
            DataRedisKey.RPS_SPOOKY,
            DataRedisKey.RPS_BEETS,
            DataRedisKey.RPS_BDEI]
    all_rps = get_reward_per_second()
    for key, rps in zip(keys, all_rps):
        print(f'{key}:\t{rps}')
        marketcap_db.set(key, rps)


@handle_error
def alloc_point_updator():
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


def run_updator():
    managers = {}
    for chain, _ in non_circulating_contracts.items():
        managers[chain] = RPCManager(chain)

    while True:
        try:
            deus_updator(managers)
            xdeus_updator(managers)
            tl_updator(managers)
            tvl_updator(managers)
            reward_per_second_updator()
            alloc_point_updator()
        except KeyboardInterrupt:
            break
        time.sleep(update_timeout)


if __name__ == '__main__':
    run_updator()
