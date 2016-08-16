import os
import requests
import time
from log import logger

common_headers = {'accept': 'application/vnd.twitchtv.v3+json'}
client_id = os.environ.get('TWITCH_CLIENT_ID', None)
if client_id:
    common_headers['Client-Id'] = client_id

KRAKEN = 'https://api.twitch.tv/kraken'
RECHAT = 'https://rechat.twitch.tv/rechat-messages'
TMI = 'https://tmi.twitch.tv'
MAX_GET = 100
MAX_RETRY = 3

LOOTS = 'https://loots.com/api/v1/'
LOOTS_MAX_GET = 500

try:
    requests.packages.urllib3.disable_warnings()
except:
    pass


class TwitchAPI(object):
    caching = None

    @staticmethod
    def set_caching(cache_interface):
        TwitchAPI.caching = cache_interface

    @staticmethod
    def get(url, payload=None):
        payload = payload or {}
        logger.debug([url, payload])
        retries = MAX_RETRY
        res = None
        while retries > 0:
            try:
                cache = TwitchAPI.caching
                if cache:
                    res = cache.get(url, payload)
                    if res:
                        return res

                res = requests.get(url, params=payload,
                                   headers=common_headers, verify=False)
                j = res.json()
                if cache:
                    cache.set(url, payload, j)

                if "error" in j and j['error']:
                    raise Exception(j.get("error"))
                return j
            except ValueError as e:
                logger.exception(e)
                if res:
                    logger.warning(res.text)
                retries -= 1
                if retries <= 0:
                    raise
                time.sleep(0.3)
            except Exception as e:
                logger.exception(e)
                raise e


def tab_print(*args):
    print "\t".join(map(unicode, args))
