import json
import time

from flask import Flask, jsonify, request

from constants import Network
from redis_client import marketcap_db, price_db
from utils import RouteName, PriceRedisKey, DataRedisKey

deus_chains = Network.deus_chains()
xdeus_chains = Network.xdeus_chains()
app = Flask(__name__)


def gradual_circulating_supply(actual_supply):
    base = 122013000000000000000000
    last_timestamp = 1674234000
    now = int(time.time())
    if now >= last_timestamp or actual_supply <= base:
        return actual_supply
    return base + int((actual_supply - base) * (1 - (((last_timestamp - now) // 360) / 2400)))


def get_marketcap_info():
    usdc_price = float(price_db.get(PriceRedisKey.USDC_KRAKEN))
    deus_price = float(marketcap_db.get(DataRedisKey.PRICE_TAG)) * usdc_price
    xdeus_price = float(marketcap_db.get(DataRedisKey.X_PRICE_TAG)) * usdc_price
    result = dict(price=dict(deus=str(deus_price), xdeus=str(xdeus_price)), result={})
    totalAmounts = dict(totalSupply=0,
                        totalSupplyOnChain=0,
                        supplyInBridges=0,
                        supplyInVeDeusContract=0,
                        nonCirculatingSupply=0,
                        circulatingSupply=0,
                        FDV=0,
                        marketCap=0)
    deus = {}
    for chain in deus_chains:
        supply = int(marketcap_db.get(DataRedisKey.TOTAL_SUPPLY + chain))
        chain_total_supply = int(marketcap_db.get(DataRedisKey.CHAIN_TOTAL_SUPPLY + chain))
        supply_in_bridges = int(marketcap_db.get(DataRedisKey.SUPPLY_IN_BRIDGE_CONTRACTS + chain))
        supply_in_vedeus = int(marketcap_db.get(DataRedisKey.SUPPLY_IN_VEDEUS_CONTRACT + chain))
        non_circulating_supply = int(marketcap_db.get(DataRedisKey.NC_SUPPLY + chain))
        circulating_supply = supply - non_circulating_supply
        fdv = round(supply * deus_price / 1e18)
        market_cap = round(circulating_supply * deus_price / 1e18)
        deus[chain] = dict(totalSupply=str(supply),
                           totalSupplyOnChain=str(chain_total_supply),
                           supplyInBridges=str(supply_in_bridges),
                           supplyInVedeusContract=str(supply_in_vedeus),
                           nonCirculatingSupply=str(non_circulating_supply),
                           circulatingSupply=str(circulating_supply),
                           FDV=str(fdv),
                           marketCap=str(market_cap))
        totalAmounts['totalSupplyOnChain'] += chain_total_supply
        totalAmounts['supplyInBridges'] += supply_in_bridges
        totalAmounts['supplyInVeDeusContract'] += supply_in_vedeus
        totalAmounts['nonCirculatingSupply'] += non_circulating_supply
        totalAmounts['totalSupply'] += supply
        totalAmounts['circulatingSupply'] += circulating_supply
        totalAmounts['FDV'] += fdv
        totalAmounts['marketCap'] += market_cap
    deus['total'] = {k: str(v) for k, v in totalAmounts.items()}

    totalAmounts = dict(totalSupply=0,
                        totalSupplyOnChain=0,
                        circulatingSupply=0,
                        supplyInBridges=0,
                        nonCirculatingSupply=0,
                        FDV=0,
                        marketCap=0)
    xdeus = {}
    for chain in xdeus_chains:
        supply = int(marketcap_db.get(DataRedisKey.X_TOTAL_SUPPLY + chain))
        chain_total_supply = int(marketcap_db.get(DataRedisKey.X_CHAIN_TOTAL_SUPPLY + chain))
        supply_in_bridges = int(marketcap_db.get(DataRedisKey.X_SUPPLY_IN_BRIDGE_CONTRACTS + chain))
        non_circulating_supply = int(marketcap_db.get(DataRedisKey.X_NC_SUPPLY + chain))
        circulating_supply = supply - non_circulating_supply
        fdv = round(supply * xdeus_price / 1e18)
        market_cap = round(circulating_supply * xdeus_price / 1e18)
        xdeus[chain] = dict(totalSupply=str(supply),
                            totalSupplyOnChain=str(chain_total_supply),
                            supplyInBridges=str(supply_in_bridges),
                            nonCirculatingSupply=str(non_circulating_supply),
                            circulatingSupply=str(circulating_supply),
                            FDV=str(fdv),
                            marketCap=str(market_cap))
        totalAmounts['totalSupplyOnChain'] += chain_total_supply
        totalAmounts['supplyInBridges'] += supply_in_bridges
        totalAmounts['totalSupply'] += supply
        totalAmounts['nonCirculatingSupply'] += non_circulating_supply
        totalAmounts['circulatingSupply'] += circulating_supply
        totalAmounts['FDV'] += fdv
        totalAmounts['marketCap'] += market_cap
    xdeus['total'] = {k: str(v) for k, v in totalAmounts.items()}

    result['result'] = dict(deus=deus, xdeus=xdeus)
    return result


@app.route('/getMarketCap')
def get_marketcap():
    result = get_marketcap_info()
    return jsonify(result)


@app.route('/deus/<route>')
def get_deus_info(route):
    if not RouteName.is_valid(route):
        return jsonify(status='error', msg='Route not found'), 404
    total_supply = 0
    circulating_supply = 0
    non_circulating_supply = 0
    price = float(marketcap_db.get(DataRedisKey.PRICE_TAG))
    for chain in deus_chains:
        supply = int(marketcap_db.get(DataRedisKey.TOTAL_SUPPLY + chain))
        nc_supply = int(marketcap_db.get(DataRedisKey.NC_SUPPLY + chain))
        circulating_supply += supply - nc_supply
        non_circulating_supply += nc_supply
        total_supply += supply

    if route == RouteName.CIRCULATING_SUPPLY:
        # gcs = gradual_circulating_supply(round(circulating_supply))
        return jsonify(round(circulating_supply))

    elif route == RouteName.TOTAL_SUPPLY:
        return jsonify(round(total_supply))

    elif route == RouteName.NON_CIRCULATING_SUPPLY:
        return jsonify(round(non_circulating_supply))

    elif route == RouteName.MARKETCAP:
        return jsonify(round(price * circulating_supply / 1e18))

    elif route == RouteName.FDV:
        return jsonify(round(price * total_supply / 1e18))

    elif route == RouteName.PRICE:
        usdc_price = float(price_db.get(PriceRedisKey.USDC_KRAKEN))
        deus_price = float(marketcap_db.get(DataRedisKey.PRICE_TAG)) * usdc_price
        return jsonify(deus_price)

    return jsonify(status='error', msg='Route not found'), 404


@app.route('/xdeus/<route>')
def get_xdeus_info(route):
    if not RouteName.is_valid(route):
        return jsonify(status='error', msg='Route not found'), 404
    total_supply = 0
    circulating_supply = 0
    non_circulating_supply = 0
    price = float(marketcap_db.get(DataRedisKey.X_PRICE_TAG))
    for chain in xdeus_chains:
        supply = int(marketcap_db.get(DataRedisKey.X_TOTAL_SUPPLY + chain))
        nc_supply = int(marketcap_db.get(DataRedisKey.X_NC_SUPPLY + chain))
        circulating_supply += supply - nc_supply
        non_circulating_supply += nc_supply
        total_supply += supply

    if route == RouteName.CIRCULATING_SUPPLY:
        return jsonify(round(circulating_supply))

    elif route == RouteName.TOTAL_SUPPLY:
        return jsonify(round(total_supply))

    elif route == RouteName.NON_CIRCULATING_SUPPLY:
        return jsonify(round(non_circulating_supply))

    elif route == RouteName.MARKETCAP:
        return jsonify(round(price * circulating_supply / 1e18))

    elif route == RouteName.FDV:
        return jsonify(round(price * total_supply / 1e18))

    elif route == RouteName.PRICE:
        usdc_price = float(price_db.get(PriceRedisKey.USDC_KRAKEN))
        xdeus_price = float(marketcap_db.get(DataRedisKey.X_PRICE_TAG)) * usdc_price
        return jsonify(xdeus_price)

    return jsonify(status='error', msg='Route not found'), 404


@app.route('/xdeus-deus/ratio')
def get_xdeus_deus_ratio():
    ratio = round(int(price_db.get(PriceRedisKey.xDEUS_RATIO)) / 1e6, 3)
    return jsonify(ratio)


@app.route('/xdeus-deus/marketcap')
def get_xdeus_deus_marketcap():
    result = get_marketcap_info()
    deus_marketcap = int(result['result']['deus']['total']['marketCap'])
    xdeus_marketcap = int(result['result']['xdeus']['total']['marketCap'])
    return jsonify(deus_marketcap + xdeus_marketcap)


@app.route('/tvl')
def get_tvl():
    usdc_price = float(price_db.get(PriceRedisKey.USDC_KRAKEN))
    deus_price = float(marketcap_db.get(DataRedisKey.PRICE_TAG)) * usdc_price
    xdeus_price = float(marketcap_db.get(DataRedisKey.X_PRICE_TAG)) * usdc_price
    xdeus_deus_tvl_ftm = round(int(marketcap_db.get(DataRedisKey.xDD_TL_FTM)) * deus_price)
    xdeus_tvl_ftm = round(int(marketcap_db.get(DataRedisKey.xD_TL_FTM)) * xdeus_price)
    xdeus_deus_tvl_eth = round(int(marketcap_db.get(DataRedisKey.xDD_TL_ETH)) * deus_price)
    return jsonify(fantom={'xDEUS-DEUS': xdeus_deus_tvl_ftm, 'xDEUS': xdeus_tvl_ftm},
                   mainnet={'xDEUS-DEUS': xdeus_deus_tvl_eth})


@app.route('/getTVL')
def get_single_tvl():
    masterchef = request.args.get('masterchef')
    pool_id = request.args.get('poolId')
    if masterchef is None:
        return jsonify(status='error', msg=f'missing param `masterchef`')
    if pool_id is None:
        return jsonify(status='error', msg=f'missing param `poolId`')

    key = None
    if masterchef == 'xdeus':
        if pool_id == '0':
            key = DataRedisKey.TVL_SINGLE_XDEUS
        elif pool_id == '2':
            key = DataRedisKey.TVL_XDEUS_DEUS
    elif masterchef == 'spooky':
        if pool_id == '0':
            key = DataRedisKey.TVL_LP_DEUS_FTM
        elif pool_id == '2':
            key = DataRedisKey.TVL_LP_DEI_USDC
    elif masterchef == 'beets':
        if pool_id == '0':
            key = DataRedisKey.TVL_BEETS_DEI_USDC
    elif masterchef == 'bdei':
        if pool_id == '0':
            key = DataRedisKey.TVL_SINGLE_BDEI
        elif pool_id == '1':
            key = DataRedisKey.TVL_DEI_BDEI
    elif masterchef == 'solidly':
        if pool_id == '0':
            key = DataRedisKey.TVL_SOLIDLY_XDEUS_DEUS
        elif pool_id == '1':
            key = DataRedisKey.TVL_SOLIDLY_WETH_DEUS
        elif pool_id == '2':
            key = DataRedisKey.TVL_SOLIDLY_WETH_DEI
        elif pool_id == '3':
            key = DataRedisKey.TVL_SOLIDLY_USDC_DEI
    else:
        return jsonify(status='error', msg=f'invalid masterchef `{masterchef}`')
    if key is None:
        return jsonify(status='error', msg=f'invalid  poolId `{pool_id}` for masterchef {masterchef}')
    return jsonify(int(marketcap_db.get(key)))


@app.route('/getRewardPerSecond')
def get_reward_per_second():
    masterchef = request.args.get('masterchef')
    if masterchef is None:
        return jsonify(status='error', msg=f'missing param `masterchef`')
    if masterchef == 'xdeus':
        key = DataRedisKey.RPS_XDEUS
    elif masterchef == 'spooky':
        key = DataRedisKey.RPS_SPOOKY
    elif masterchef == 'beets':
        key = DataRedisKey.RPS_BEETS
    elif masterchef == 'bdei':
        key = DataRedisKey.RPS_BDEI
    else:
        return jsonify(status='error', msg=f'invalid masterchef `{masterchef}`')
    return jsonify(int(marketcap_db.get(key)))


@app.route('/getAllocPoint')
def get_alloc_point():
    masterchef = request.args.get('masterchef')
    pool_id = request.args.get('poolId')
    if masterchef is None:
        return jsonify(status='error', msg=f'missing param `masterchef`')
    if pool_id is None:
        return jsonify(status='error', msg=f'missing param `poolId`')

    key = None
    if masterchef == 'xdeus':
        if pool_id == '0':
            key = DataRedisKey.AP_SINGLE_XDEUS
        elif pool_id == '2':
            key = DataRedisKey.AP_XDEUS_DEUS
    elif masterchef == 'spooky':
        if pool_id == '0':
            key = DataRedisKey.AP_LP_DEUS_FTM
        elif pool_id == '2':
            key = DataRedisKey.AP_LP_DEI_USDC
    elif masterchef == 'beets':
        if pool_id == '0':
            key = DataRedisKey.AP_BEETS_DEI_USDC
    elif masterchef == 'bdei':
        if pool_id == '0':
            key = DataRedisKey.AP_SINGLE_BDEI
        elif pool_id == '1':
            key = DataRedisKey.AP_DEI_BDEI
    else:
        return jsonify(status='error', msg=f'invalid masterchef `{masterchef}`')
    if key is None:
        return jsonify(status='error', msg=f'invalid  poolId `{pool_id}` for masterchef {masterchef}')
    return jsonify(int(marketcap_db.get(key)))


@app.route('/dei/price')
def get_dei_price():
    value = price_db.get(PriceRedisKey.DEI_FIREBIRD)
    if value == b'N/A':
        price = 1.0
    else:
        price = round(int(value) / 1e6, 3)
    return jsonify(price)


@app.route('/dei/reserves')
def get_dei_reserves():
    reserves = int(marketcap_db.get(DataRedisKey.DEI_RESERVES))
    return jsonify(reserves)


@app.route('/dei/reserves/detail')
def get_dei_reserves_detail():
    info = json.loads(marketcap_db.get(DataRedisKey.DEI_JSON_RESERVES))
    return jsonify(info)


@app.route('/dei/getDeiStats')
def get_dei_stats():
    # dei_price = price_db.get(PriceRedisKey.DEI_FIREBIRD)
    total_supply = int(marketcap_db.get(DataRedisKey.DEI_CIRCULATING_SUPPLY))
    circulating_supply = total_supply
    reserves = json.loads(marketcap_db.get(DataRedisKey.DEI_JSON_RESERVES))
    total_reserves = int(marketcap_db.get(DataRedisKey.DEI_RESERVES))
    usdc_backing_per_dei = round(total_reserves * 1e18 / total_supply, 3)
    dei_seigniorage_ratio = round(int(marketcap_db.get(DataRedisKey.DEI_SEIGNIORAGE_RATIO)) * 100 / 1e6, 3)
    return jsonify({'usdcBackingPerDei': str(usdc_backing_per_dei),
                    'deiSeigniorageRatio': str(dei_seigniorage_ratio),
                    'totalSupply': str(total_supply),
                    'circulatingSupply': str(circulating_supply),
                    'reserves': reserves})


@app.route('/dei/circulating-supply')
def get_dei_circ_supply():
    supply = int(marketcap_db.get(DataRedisKey.DEI_CIRCULATING_SUPPLY))
    return jsonify(supply)


@app.route('/dei/allChainsTotalSupply')
def get_dei_total_supply():
    supply = int(marketcap_db.get(DataRedisKey.DEI_TOTAL_SUPPLY))
    return jsonify(supply)


@app.route('/getPrices')
def get_prices():
    keys = [
        PriceRedisKey.DEUS_SPOOKY,
        PriceRedisKey.DEUS_SPIRIT,
        PriceRedisKey.DEUS_SOLIDLY_ETH,
        PriceRedisKey.DEI_FIREBIRD,
        PriceRedisKey.DEI_SOLIDLY_ETH,
        PriceRedisKey.legacyDEI_SPOOKY,
        PriceRedisKey.legacyDEI_SPIRIT,
        PriceRedisKey.legacyDEI_SOLIDLY,
        PriceRedisKey.legacyDEI_BEETS,
    ]
    prices = []
    for key in keys:
        value = price_db.get(key)
        if value is None or value.decode() == 'N/A':
            price = 'N/A'
        else:
            price = str(round(int(value) / 1e6, 6))
        prices.append(price)
    for key in [PriceRedisKey.DEUS_GATEIO, PriceRedisKey.DEUS_MEXC]:
        value = price_db.get(key)
        if value:
            price = value.decode()
        else:
            price = 'N/A'
        prices.append(price)
    deus = []
    dei = []
    legacy_dei = []
    deus.append(dict(price=prices[0], source='spookySwap'))
    deus.append(dict(price=prices[1], source='spiritSwap'))
    deus.append(dict(price=prices[2], source='solidly(ETH)'))
    dei.append(dict(price=prices[3], source='firebird'))
    dei.append(dict(price=prices[4], source='solidly(ETH)'))
    legacy_dei.append(dict(price=prices[5], source='spookySwap'))
    legacy_dei.append(dict(price=prices[6], source='spiritSwap'))
    legacy_dei.append(dict(price=prices[7], source='solidly(FTM)'))
    legacy_dei.append(dict(price=prices[8], source='beethovenX'))
    deus.append(dict(price=prices[9], source='gateio'))
    deus.append(dict(price=prices[10], source='mexc'))
    usdc_price = float(price_db.get(PriceRedisKey.USDC_KRAKEN))
    usdc = [dict(price=str(usdc_price), source='kraken')]
    return jsonify(usdc=usdc, deus=deus, dei=dei, legacyDei=legacy_dei)


@app.route('/deusPerWeek')
def get_deus_per_week():
    try:
        deus_per_week = float(marketcap_db.get(DataRedisKey.DEUS_PER_WEEK))
    except:
        return jsonify(status='error', msg='N/A'), 400
    return jsonify(deus_per_week), 200


if __name__ == '__main__':
    app.run(port=5152)
