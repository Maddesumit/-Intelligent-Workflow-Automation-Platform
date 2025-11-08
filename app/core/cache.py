"""Redis cache configuration."""
import redis.asyncio as aioredis
from app.config import settings


class RedisCache:
    """Redis cache manager."""
    
    def __init__(self):
        self.redis: aioredis.Redis = None
    
    async def connect(self):
        """Connect to Redis."""
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str):
        """Get value from cache."""
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: int = None):
        """Set value in cache."""
        await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        """Delete key from cache."""
        await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self.redis.exists(key)


# Global cache instance
cache = RedisCache()
