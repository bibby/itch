import os
from cache import CacheInterface, logger
import memcache


class MemcacheCache(CacheInterface):

    servers = os.environ.get('MEMCACHE_SERVERS', '127.0.0.1:11211')
    mc = memcache.Client([s.strip() for s in servers.split(',')], debug=0)

    def get_value(self, key):
        val = MemcacheCache.mc.get(key)
        if val:
            logger.debug('CacheHit: ' + key)
            return val

        logger.debug('CacheMiss: ' + key)

    def set_value(self, key, value=None):
        logger.debug('CacheWrite: ' + key)
        return MemcacheCache.mc.set(key, value)
