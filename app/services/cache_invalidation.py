from app.redis.confredis import redis_client


def cache_invalidation(url: str):
    redis_client.delete(url)
