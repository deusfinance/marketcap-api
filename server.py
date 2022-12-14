from flask import Flask, jsonify

from constants import non_circulating_contracts
from config import PRICE_REDIS_TAG, REDIS_PREFIX
from redis_client import redis_client

chains = list(non_circulating_contracts)
app = Flask(__name__)


@app.route('/getMarketCap')
def get_market_cap():
    price = float(redis_client.get(PRICE_REDIS_TAG))
    res = {}
    for chain in chains:
        res[chain] = round(int(redis_client.get(REDIS_PREFIX + chain)) * price)
    return res


@app.route('/getCirculatingSupplies')
def get_circulating_supplies():
    res = {}
    for chain in chains:
        res[chain] = int(redis_client.get(REDIS_PREFIX + chain))
    return res


@app.route('/circulatingSupply/<chain>')
def get_circulating_supply(chain):
    if chain.lower() not in chains:
        return jsonify(status='error', msg=f'Invalid chain: `{chain}`'), 400

    market_cap = int(redis_client.get(REDIS_PREFIX + chain.lower()))
    return jsonify(status='ok', chain=chain.lower(), marketCap=market_cap), 200
