import os
import re
from cache import CacheInterface, logger


class FileTreeCache(CacheInterface):
    tmp_dir = os.environ.get("TWITCH_CACHE_TEMP", "/tmp/itch")

    @staticmethod
    def get_cache_filename(key):
        return os.path.join(
            FileTreeCache.tmp_dir,
            *re.findall('..', key) + ['v']
        )

    def get_value(self, key):
        cache_file = FileTreeCache.get_cache_filename(key)
        if os.path.isfile(cache_file):
            logger.debug('CacheHit: ' + key)
            with open(cache_file, 'r') as f:
                return f.read()
        logger.debug('CacheMiss: ' + key)

    def set_value(self, key, value=None):
        cache_file = FileTreeCache.get_cache_filename(key)
        cache_dir = os.path.dirname(cache_file)
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)

        with open(cache_file, 'w') as f:
            logger.debug('CacheWrite: ' + key)
            f.write(value)
