from flask import Flask, jsonify

from configs import chain_configs, redis_prefix
from redis_client import redis_client

app = Flask(__name__)


@app.route("/getMarketCaps")
def get_market_caps():
    res = {}
    for chain, config in chain_configs.items():
        res[chain] = int(redis_client.get(redis_prefix + chain))
    return res


@app.route("/marketCap/<chain>")
def get_market_caps(chain):
    if chain.lower() not in chain_configs:
        return jsonify(status='error', msg=f'Invalid chain: `{chain}`'), 400

    market_cap = int(redis_client.get(redis_prefix + chain.lower()))
    return jsonify(status='ok', chain=chain.lower(), marketCap=market_cap), 200
