import redis

from config import REDIS_MARKETCAP_DB, REDIS_PRICE_DB

marketcap_db = redis.Redis(db=REDIS_MARKETCAP_DB)
price_db = redis.Redis(db=REDIS_PRICE_DB)
