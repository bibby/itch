import hashlib
import json
import os
import zlib
import logging
from itch.log import logger


class CacheInterface(object):
    def get(self, base_url, query_params=None):
        key = self.get_key(base_url, query_params)
        val = self.get_value(key)
        if val:
            return Compression.decompress(val)

    def get_value(self, key):
        raise Exception("Method not implemented")

    def set(self, base_url, query_params=None, value=None):
        key = self.get_key(base_url, query_params)
        return self.set_value(key, Compression.compress(value))

    def set_value(self, key, value):
        raise Exception("Method not implemented")

    def get_key(self, base_url, query_params):
        query_params = query_params or {}
        query_string = []
        for key in sorted(query_params):
            query_string.append("%s=%s" % (key, query_params[key]))
        return hashlib.sha256("%s|%s" % (base_url, query_string)).hexdigest()


class Compression(object):
    @staticmethod
    def compress(data):
        return zlib.compress(json.dumps(data))

    @staticmethod
    def decompress(data):
        return json.loads(zlib.decompress(data))
