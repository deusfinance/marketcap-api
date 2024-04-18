import json
import re

from flask import Flask, jsonify, request

from settings import Network, DEUS_FIXED_TOTAL_SUPPLY
from redis_client import marketcap_db, price_db
from utils import RouteName, PriceRedisKey, DataRedisKey, get_deus_remaining

deus_chains = Network.deus_chains()
xdeus_chains = Network.xdeus_chains()
app = Flask(__name__)


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
        chain_total_supply = int(marketcap_db.get(DataRedisKey.CHAIN_TOTAL_SUPPLY + chain))
        non_circulating_supply = int(marketcap_db.get(DataRedisKey.NC_SUPPLY + chain))
        circulating_supply = chain_total_supply - non_circulating_supply
        deus[chain] = dict(totalSupply=str(chain_total_supply),
                           totalSupplyOnChain=str(chain_total_supply),
                           supplyInBridges=str(0),
                           supplyInVedeusContract=str(0),
                           nonCirculatingSupply=str(non_circulating_supply),
                           circulatingSupply=str(circulating_supply),
                           FDV=str(0),
                           marketCap=str(0))
        totalAmounts['totalSupplyOnChain'] += chain_total_supply
        totalAmounts['nonCirculatingSupply'] += non_circulating_supply
        totalAmounts['circulatingSupply'] += circulating_supply

    deus_remaining = get_deus_remaining()
    if deus_remaining:
        totalAmounts['circulatingSupply'] = deus_remaining

    totalAmounts['totalSupply'] = DEUS_FIXED_TOTAL_SUPPLY
    totalAmounts['FDV'] = round(DEUS_FIXED_TOTAL_SUPPLY * deus_price / 1e18)
    totalAmounts['marketCap'] = round(totalAmounts['circulatingSupply'] * deus_price / 1e18)
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
        chain_total_supply = int(marketcap_db.get(DataRedisKey.X_CHAIN_TOTAL_SUPPLY + chain))
        non_circulating_supply = int(marketcap_db.get(DataRedisKey.X_NC_SUPPLY + chain))
        circulating_supply = chain_total_supply - non_circulating_supply
        xdeus[chain] = dict(totalSupply=str(chain_total_supply),
                            totalSupplyOnChain=str(chain_total_supply),
                            supplyInBridges=str(0),
                            nonCirculatingSupply=str(non_circulating_supply),
                            circulatingSupply=str(circulating_supply),
                            FDV=str(0),
                            marketCap=str(0))
        totalAmounts['totalSupplyOnChain'] += chain_total_supply
        totalAmounts['nonCirculatingSupply'] += non_circulating_supply
        totalAmounts['circulatingSupply'] += circulating_supply
    totalAmounts['totalSupply'] = totalAmounts['totalSupplyOnChain']
    totalAmounts['FDV'] = round(totalAmounts['totalSupply'] * xdeus_price / 1e18)
    totalAmounts['marketCap'] += round(totalAmounts['circulatingSupply'] * xdeus_price / 1e18)
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
    price = float(marketcap_db.get(DataRedisKey.PRICE_TAG))
    non_circulating_supply = 0
    chain_total_supply = 0
    for chain in deus_chains:
        non_circulating_supply += int(marketcap_db.get(DataRedisKey.NC_SUPPLY + chain))
        chain_total_supply += int(marketcap_db.get(DataRedisKey.CHAIN_TOTAL_SUPPLY + chain))
    circulating_supply = chain_total_supply - non_circulating_supply

    deus_remaining = get_deus_remaining()
    if deus_remaining:
        circulating_supply = deus_remaining

    total_supply = DEUS_FIXED_TOTAL_SUPPLY
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
        deus_price = float(marketcap_db.get(DataRedisKey.PRICE_TAG)) * usdc_price
        return jsonify(deus_price)

    return jsonify(status='error', msg='Route not found'), 404


@app.route('/xdeus/<route>')
def get_xdeus_info(route):
    if not RouteName.is_valid(route):
        return jsonify(status='error', msg='Route not found'), 404
    price = float(marketcap_db.get(DataRedisKey.X_PRICE_TAG))
    non_circulating_supply = 0
    total_supply = 0
    for chain in xdeus_chains:
        non_circulating_supply += int(marketcap_db.get(DataRedisKey.X_NC_SUPPLY + chain))
        total_supply += int(marketcap_db.get(DataRedisKey.X_CHAIN_TOTAL_SUPPLY + chain))
    circulating_supply = total_supply - non_circulating_supply
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


@app.route('/dei/price')
def get_dei_price():
    value = price_db.get(PriceRedisKey.DEI_FIREBIRD)
    if value == b'N/A':
        price = 1.0
    else:
        price = round(int(value) / 1e6, 3)
    return jsonify(price)


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


with open('dei_users_data.json') as fp:
    dei_users_data = json.load(fp)


@app.route('/dei/userData/<address>')
def get_dei_user_data(address: str):
    address = address.lower()
    if re.match(r'^0x[0-9a-f]{40}$', address) and int(address, 16):
        data = dei_users_data.get(address)
        if data:
            return jsonify(data)
        return jsonify(status='error', msg='user with this address not found')
    return jsonify(status='error', msg='invalid address')


if __name__ == '__main__':
    app.run(port=5152)
