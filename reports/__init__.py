from itch import TwitchAPI, tab_print
from itch.models import Channel, User
from itch.times import subtime


def print_followers(channel, caching=None, count_following=None,
                    limit=None, return_lines=None):
    if caching:
        TwitchAPI.set_caching(caching)

    c = Channel.get(channel)
    for f in c.list_followers(direction='DESC', limit=limit):
        u = f.user
        d = [
            u.name,
            channel,
            u.created_at,
            f.created_at,
            subtime(u.created_at, f.created_at)
        ]

        if count_following:
            d.append(u.count_following())

        if return_lines:
            return d

        tab_print(*d)


def print_following(user, caching=None, count_following=None,
                    return_lines=None):
    if caching:
        TwitchAPI.set_caching(caching)

    u = User.get(user)
    if count_following:
        following = u.count_following()

    for f in u.list_following(direction='DESC'):
        c = f.channel
        d = [
            u.name,
            c.name,
            u.created_at,
            f.created_at,
        ]

        if count_following:
            d.append(following)

        if return_lines:
            return d

        tab_print(*d)
