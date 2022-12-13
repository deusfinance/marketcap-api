from flask import Flask

from configs import chain_configs
from redis_client import redis_client

app = Flask(__name__)


@app.route("/")
def get_market_caps():
    res = {}
    for chain, config in chain_configs.items():
        res[chain] = int(redis_client.get(chain))
    return res
