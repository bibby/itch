from itch import TwitchAPI, tab_print
from itch.models import Channel, User
from itch.times import subtime, to_timestamp


def print_followers(channel, caching=None, count_following=None,
                    limit=None, direction=None, return_lines=None,
                    **kwargs):
    caching = __get_cache(caching)
    if caching:
        TwitchAPI.set_caching(caching)

    direction = direction or 'DESC'

    c = Channel.get(channel)
    for f in c.list_followers(direction=direction.upper(), limit=limit):
        u = f.user
        d = [
            u.name,
            channel,
            to_timestamp(u.created_at),
            to_timestamp(f.created_at),
            subtime(u.created_at, f.created_at)
        ]

        if count_following:
            d.append(u.count_following())

        if return_lines:
            return d

        tab_print(*d)


def print_following(channel, caching=None, count_following=None,
                    limit=None, direction=None, return_lines=None,
                    **kwargs):

    caching = __get_cache(caching)
    if caching:
        TwitchAPI.set_caching(caching)

    direction = direction or 'DESC'

    u = User.get(channel)
    if count_following:
        following = u.count_following()

    for f in u.list_following(direction=direction.upper(), limit=limit):
        c = f.channel
        d = [
            u.name,
            c.name,
            to_timestamp(u.created_at),
            to_timestamp(f.created_at),
            subtime(u.created_at, f.created_at)
        ]

        if count_following:
            d.append(following)

        if return_lines:
            return d

        tab_print(*d)


def loots_streams(channel=None, caching=None, limit=None,
                  direction=None, **kwargs):
    __assert_args(channel)

    caching = __get_cache(caching)
    if caching:
        TwitchAPI.set_caching(caching)

    channel = Channel.get(channel)
    for stream in channel.loots_streams(limit=limit, direction=direction):
        tab_print(stream.t_start, stream.t_end)


def chatters(channel=None, caching=None, **kwargs):
    __assert_args(channel)

    caching = __get_cache(caching)
    if caching:
        TwitchAPI.set_caching(caching)

    channel = Channel.get(channel)
    chatters = channel.get_chatters()
    for name in chatters.moderators:
        print name
    for name in chatters.viewers:
        print name


def __assert_args(channel=None, **kwargs):
    if not channel:
        raise Exception('Channel not given')


def __get_cache(cache):
    if cache == 'file':
        from cache.filetree import FileTreeCache
        return FileTreeCache()
    if cache == 'redis':
        from cache.rcache import RedisCache
        return RedisCache()
    if cache == 'memcache':
        from cache.mcache import MemcacheCache
        return MemcacheCache()
