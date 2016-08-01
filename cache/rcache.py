import os
from cache import CacheInterface, logger
from redis import StrictRedis


class RedisCache(CacheInterface):

    red = StrictRedis(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        password=os.environ.get('REDIS_PASSWORD', None),
        db=os.environ.get('REDIS_DB', 1)
    )

    def get_value(self, key):
        val = RedisCache.red.get(key)
        if val:
            logger.debug('CacheHit: ' + key)
            return val

        logger.debug('CacheMiss: ' + key)

    def set_value(self, key, value=None):
        logger.debug('CacheWrite: ' + key)
        return RedisCache.red.set(key, value)
