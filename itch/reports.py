from itch import TwitchAPI, tab_print
from itch.models import Channel, User, Video
from itch.times import subtime, to_timestamp


def print_followers(channel, count_following=None,
                    limit=None, direction=None, return_lines=None,
                    **kwargs):
    __set_caching(**kwargs)
    direction = direction or 'DESC'

    c = Channel.get(channel)
    for f in c.list_followers(direction=direction.upper(), limit=limit):
        u = f.user
        d = [
            u.name,
            channel,
            to_timestamp(u.created_at),
            to_timestamp(f.created_at),
            subtime(u.created_at, f.created_at),
            0,
        ]

        if count_following:
            d.append(u.count_following())

        if return_lines:
            return d

        tab_print(*d)


def print_following(channel, count_following=None,
                    limit=None, direction=None, return_lines=None,
                    **kwargs):

    __set_caching(**kwargs)
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
            subtime(u.created_at, f.created_at),
            c.followers,
        ]

        if count_following:
            d.append(following)

        if return_lines:
            return d

        tab_print(*d)


def loots_streams(channel=None, limit=None,
                  direction=None, **kwargs):
    __assert_args(channel)
    __set_caching(**kwargs)

    channel = Channel.get(channel)
    for stream in channel.loots_streams(limit=limit, direction=direction):
        tab_print(stream.t_start, stream.t_end)


def chatters(channel=None, **kwargs):
    __assert_args(channel)
    __set_caching(**kwargs)

    channel = Channel.get(channel)
    chatters = channel.get_chatters()
    for name in chatters.moderators:
        print name
    for name in chatters.viewers:
        print name


def created(channel=None, **kwargs):
    __assert_args(channel)
    __set_caching(**kwargs)

    channel = Channel.get(channel)
    tab_print(channel.name, to_timestamp(channel.created_at))


def following(channel=None, **kwargs):
    __assert_args(channel)
    __set_caching(**kwargs)

    channel = User(name=channel)
    tab_print(channel.name, channel.count_following())


def followers(channel=None, **kwargs):
    __assert_args(channel)
    __set_caching(**kwargs)

    channel = Channel.get(channel)
    tab_print(channel.name, channel.followers)


def chatlog(channel, **kwargs):
    video = Video.get(channel)
    for m in video.chat_replay():
        try:
            print u" : ".join([
                m['from'].encode('utf8'),
                m.message.encode('utf8')]
            )
        except:
            print "ERR <unprintable>"


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


def __set_caching(**kwargs):
    caching = __get_cache(kwargs.get('caching'))
    if caching:
        TwitchAPI.set_caching(caching)

reports = dict(
    followers=print_followers,
    following=print_following,
    loots_streams=loots_streams,
    chatters=chatters,
    chatlog=chatlog,
    created=created,
    num_following=following,
    num_followers=followers,
)
