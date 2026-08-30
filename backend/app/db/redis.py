import redis
from app.core.config import settings

def get_redis_client() -> redis.Redis:
    """Get a connected Redis client based on application settings."""
    return redis.from_url(settings.redis_url, decode_responses=True)

def ping_redis() -> bool:
    """Ping Redis to check connectivity."""
    try:
        client = get_redis_client()
        return client.ping()
    except redis.RedisError:
        return False
