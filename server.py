from flask import Flask, jsonify

from constants import non_circulating_contracts
from config import PRICE_REDIS_TAG, NC_SUPPLY_REDIS_PREFIX, TOTAL_SUPPLY_REDIS_PREFIX
from redis_client import redis_client

chains = list(non_circulating_contracts)
app = Flask(__name__)


@app.route('/getMarketCap')
def get_market_cap():
    price = float(redis_client.get(PRICE_REDIS_TAG))
    result = dict(deusPrice=str(price), result={})
    totalAmounts = dict(totalSupply=0,
                        circulatingSupply=0,
                        FDV=0,
                        MarketCap=0)
    for chain in chains:
        supply = int(redis_client.get(TOTAL_SUPPLY_REDIS_PREFIX + chain))
        circulating_supply = supply - int(redis_client.get(NC_SUPPLY_REDIS_PREFIX + chain))
        fdv = round(supply * price / 1e18)
        market_cap = round(circulating_supply * price / 1e18)
        result['result'][chain] = dict(totalSupply=str(supply),
                                       circulatingSupply=str(circulating_supply),
                                       FDV=str(fdv),
                                       MarketCap=str(market_cap))
        totalAmounts['totalSupply'] += supply
        totalAmounts['circulatingSupply'] += circulating_supply
        totalAmounts['FDV'] += fdv
        totalAmounts['MarketCap'] += market_cap

    result['result']['total'] = {k: str(v) for k, v in totalAmounts.items()}
    return jsonify(result)


@app.route('/getCirculatingSupplies')
def get_circulating_supplies():
    res = {}
    for chain in chains:
        res[chain] = int(redis_client.get(NC_SUPPLY_REDIS_PREFIX + chain))
    return jsonify(res)


@app.route('/circulatingSupply/<chain>')
def get_circulating_supply(chain):
    if chain.lower() not in chains:
        return jsonify(status='error', msg=f'Invalid chain: `{chain}`'), 400

    market_cap = int(redis_client.get(NC_SUPPLY_REDIS_PREFIX + chain.lower()))
    return jsonify(status='ok', chain=chain.lower(), marketCap=market_cap), 200
