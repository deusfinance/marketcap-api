from flask import Flask, jsonify

from constants import non_circulating_contracts, xdeus_non_circulating_contracts
from config import PRICE_REDIS_TAG, NC_SUPPLY_REDIS_PREFIX, TOTAL_SUPPLY_REDIS_PREFIX, X_NC_SUPPLY_REDIS_PREFIX, \
    X_TOTAL_SUPPLY_REDIS_PREFIX, X_PRICE_REDIS_TAG
from redis_client import marketcap_db, price_db
from utils import RouteName, RedisKey

deus_chains = list(non_circulating_contracts)
xdeus_chains = list(xdeus_non_circulating_contracts)
app = Flask(__name__)


def get_marketcap_info():
    deus_price = float(marketcap_db.get(PRICE_REDIS_TAG))
    xdeus_price = float(marketcap_db.get(X_PRICE_REDIS_TAG))
    result = dict(price=dict(deus=str(deus_price), xdeus=str(xdeus_price)), result={})
    totalAmounts = dict(totalSupply=0,
                        circulatingSupply=0,
                        FDV=0,
                        marketCap=0)
    deus = {}
    for chain in deus_chains:
        supply = int(marketcap_db.get(TOTAL_SUPPLY_REDIS_PREFIX + chain))
        circulating_supply = supply - int(marketcap_db.get(NC_SUPPLY_REDIS_PREFIX + chain))
        fdv = round(supply * deus_price / 1e18)
        market_cap = round(circulating_supply * deus_price / 1e18)
        deus[chain] = dict(totalSupply=str(supply),
                           circulatingSupply=str(circulating_supply),
                           FDV=str(fdv),
                           marketCap=str(market_cap))
        totalAmounts['totalSupply'] += supply
        totalAmounts['circulatingSupply'] += circulating_supply
        totalAmounts['FDV'] += fdv
        totalAmounts['marketCap'] += market_cap
    deus['total'] = {k: str(v) for k, v in totalAmounts.items()}

    totalAmounts = dict(totalSupply=0,
                        circulatingSupply=0,
                        FDV=0,
                        marketCap=0)
    xdeus = {}
    for chain in xdeus_chains:
        supply = int(marketcap_db.get(X_TOTAL_SUPPLY_REDIS_PREFIX + chain))
        circulating_supply = supply - int(marketcap_db.get(X_NC_SUPPLY_REDIS_PREFIX + chain))
        fdv = round(supply * xdeus_price / 1e18)
        market_cap = round(circulating_supply * xdeus_price / 1e18)
        xdeus[chain] = dict(totalSupply=str(supply),
                            circulatingSupply=str(circulating_supply),
                            FDV=str(fdv),
                            marketCap=str(market_cap))
        totalAmounts['totalSupply'] += supply
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
    price = float(marketcap_db.get(PRICE_REDIS_TAG))
    for chain in deus_chains:
        supply = int(marketcap_db.get(TOTAL_SUPPLY_REDIS_PREFIX + chain))
        circulating_supply += supply - int(marketcap_db.get(NC_SUPPLY_REDIS_PREFIX + chain))
        total_supply += supply

    if route == RouteName.CIRCULATING_SUPPLY:
        return jsonify(round(circulating_supply))

    elif route == RouteName.TOTAL_SUPPLY:
        return jsonify(round(total_supply))

    elif route == RouteName.MARKETCAP:
        return jsonify(round(price * circulating_supply / 1e18))

    elif route == RouteName.FDV:
        return jsonify(round(price * total_supply / 1e18))

    elif route == RouteName.PRICE:
        deus_price = float(marketcap_db.get(PRICE_REDIS_TAG))
        return jsonify(deus_price)

    return jsonify(status='error', msg='Route not found'), 404


@app.route('/xdeus/<route>')
def get_xdeus_info(route):
    if not RouteName.is_valid(route):
        return jsonify(status='error', msg='Route not found'), 404
    total_supply = 0
    circulating_supply = 0
    price = float(marketcap_db.get(X_PRICE_REDIS_TAG))
    for chain in xdeus_chains:
        supply = int(marketcap_db.get(X_TOTAL_SUPPLY_REDIS_PREFIX + chain))
        circulating_supply += supply - int(marketcap_db.get(X_NC_SUPPLY_REDIS_PREFIX + chain))
        total_supply += supply

    if route == RouteName.CIRCULATING_SUPPLY:
        return jsonify(round(circulating_supply))

    elif route == RouteName.TOTAL_SUPPLY:
        return jsonify(round(total_supply))

    elif route == RouteName.MARKETCAP:
        return jsonify(round(price * circulating_supply / 1e18))

    elif route == RouteName.FDV:
        return jsonify(round(price * total_supply / 1e18))

    elif route == RouteName.PRICE:
        xdeus_price = float(marketcap_db.get(X_PRICE_REDIS_TAG))
        return jsonify(xdeus_price)

    return jsonify(status='error', msg='Route not found'), 404


@app.route('/xdeus-deus/ratio')
def get_xdeus_deus_ratio():
    ratio = round(int(price_db.get(RedisKey.xDEUS_RATIO)) / 1e6, 3)
    return jsonify(ratio)


@app.route('/xdeus-deus/marketcap')
def get_xdeus_deus_marketcap():
    result = get_marketcap_info()
    deus_marketcap = int(result['result']['deus']['total']['marketCap'])
    xdeus_marketcap = int(result['result']['xdeus']['total']['marketCap'])
    return jsonify(deus_marketcap + xdeus_marketcap)


@app.route('/dei/price')
def get_dei_price():
    price = round(int(price_db.get(RedisKey.DEI_FIREBIRD)) / 1e6, 3)
    return jsonify(price)


@app.route('/getPrices')
def get_prices():
    keys = [
        RedisKey.DEUS_SPOOKY,
        RedisKey.DEUS_SPIRIT,
        RedisKey.DEUS_SOLIDLY_ETH,
        RedisKey.DEI_FIREBIRD,
        RedisKey.DEI_SOLIDLY_ETH,
        RedisKey.legacyDEI_SPOOKY,
        RedisKey.legacyDEI_SPIRIT,
        RedisKey.legacyDEI_SOLIDLY,
        RedisKey.legacyDEI_BEETS,
    ]
    prices = []
    for key in keys:
        value = price_db.get(key)
        if value is None or value.decode() == 'N/A':
            price = 'N/A'
        else:
            price = str(round(int(value) / 1e6, 6))
        prices.append(price)
    for key in [RedisKey.DEUS_GATEIO, RedisKey.DEUS_MEXC]:
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

    return jsonify(deus=deus, dei=dei, legacyDei=legacy_dei)


if __name__ == '__main__':
    app.run(port=5152)
