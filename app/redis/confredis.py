import redis  # type: ignore

redis_client = redis.Redis(host='redis_cmenu_d', port=6378, db=0)
