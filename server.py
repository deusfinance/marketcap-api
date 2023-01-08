from flask import Flask, jsonify

from constants import non_circulating_contracts, xdeus_non_circulating_contracts
from config import PRICE_REDIS_TAG, NC_SUPPLY_REDIS_PREFIX, TOTAL_SUPPLY_REDIS_PREFIX, X_NC_SUPPLY_REDIS_PREFIX, \
    X_TOTAL_SUPPLY_REDIS_PREFIX, X_PRICE_REDIS_TAG
from redis_client import redis_client
from utils import RouteName

deus_chains = list(non_circulating_contracts)
xdeus_chains = list(xdeus_non_circulating_contracts)
app = Flask(__name__)


@app.route('/getMarketCap')
def get_market_cap():
    deus_price = float(redis_client.get(PRICE_REDIS_TAG))
    xdeus_price = float(redis_client.get(X_PRICE_REDIS_TAG))
    result = dict(price=dict(deus=str(deus_price), xdeus=str(xdeus_price)), result={})
    totalAmounts = dict(totalSupply=0,
                        circulatingSupply=0,
                        FDV=0,
                        marketCap=0)
    deus = {}
    for chain in deus_chains:
        supply = int(redis_client.get(TOTAL_SUPPLY_REDIS_PREFIX + chain))
        circulating_supply = supply - int(redis_client.get(NC_SUPPLY_REDIS_PREFIX + chain))
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
        supply = int(redis_client.get(X_TOTAL_SUPPLY_REDIS_PREFIX + chain))
        circulating_supply = supply - int(redis_client.get(X_NC_SUPPLY_REDIS_PREFIX + chain))
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
    return jsonify(result)


@app.route('/deus/<route>')
def get_deus_info(route):
    if not RouteName.is_valid(route):
        return jsonify(status='error', msg='Route not found'), 404
    total_supply = 0
    circulating_supply = 0
    price = float(redis_client.get(PRICE_REDIS_TAG))
    for chain in deus_chains:
        supply = int(redis_client.get(TOTAL_SUPPLY_REDIS_PREFIX + chain))
        circulating_supply += supply - int(redis_client.get(NC_SUPPLY_REDIS_PREFIX + chain))
        total_supply += supply

    if route == RouteName.CIRCULATING_SUPPLY:
        return jsonify(round(circulating_supply))

    elif route == RouteName.TOTAL_SUPPLY:
        return jsonify(round(total_supply))

    elif route == RouteName.MARKETCAP:
        return jsonify(round(price * circulating_supply / 1e18))

    elif route == RouteName.FDV:
        return jsonify(round(price * total_supply / 1e18))

    return jsonify(status='error', msg='Route not found'), 404


@app.route('/xdeus/<route>')
def get_xdeus_info(route):
    if not RouteName.is_valid(route):
        return jsonify(status='error', msg='Route not found'), 404
    total_supply = 0
    circulating_supply = 0
    price = float(redis_client.get(X_PRICE_REDIS_TAG))
    for chain in xdeus_chains:
        supply = int(redis_client.get(X_TOTAL_SUPPLY_REDIS_PREFIX + chain))
        circulating_supply += supply - int(redis_client.get(X_NC_SUPPLY_REDIS_PREFIX + chain))
        total_supply += supply

    if route == RouteName.CIRCULATING_SUPPLY:
        return jsonify(round(circulating_supply))

    elif route == RouteName.TOTAL_SUPPLY:
        return jsonify(round(total_supply))

    elif route == RouteName.MARKETCAP:
        return jsonify(round(price * circulating_supply / 1e18))

    elif route == RouteName.FDV:
        return jsonify(round(price * total_supply / 1e18))

    return jsonify(status='error', msg='Route not found'), 404


if __name__ == '__main__':
    app.run(port=5152)
