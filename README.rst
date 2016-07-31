itch
====

A python module for pulling data from the Twitch.tv APIs (kraken, tmi, rechat).

Install
-------

::

    pip install itch

Config
------

Starting in August 2016, the kraken API will `require an application client id <https://discuss.dev.twitch.tv/t/client-id-will-be-required-in-august/6032/9>`_.
If the environment variable ``TWITCH_CLIENT_ID`` is set, itch will use this. There is no default value, but you can use the APIs without one until August;
after which you will have to supply your own.


Models
------

itch models wrap their own API endpoints, so most items can be loaded by name using the static ``get`` method, and used as dictionaries.
It'd be wise to familiarize yourself with the return values from the `kraken v3 resources <https://github.com/justintv/Twitch-API/tree/master/v3_resources>`_,
as most keys (like ``id`` and ``name``) are not explicitly mentioned in the module, but read from json and made into a ``dict``.

::

    >>> from itch.models import Channel
    >>> c = Channel.get('itmejp')
    >>> c.followers
    248650
    >>> c.created_at
    datetime.datetime(2010, 2, 28, 9, 30, 51)


All dates are made into timezone-absent ``datetime`` instances. Nested objects are usually rolled into specialized classes of their own.


Generators
----------

Lists of objects, where API paging is involved is done through generators, allowing you to seamlessly iterate over every item of a collection.

::
    >>> for follow in c.list_following():
    ...     print follow.created_at, follow.channel.name
    ...
    2011-03-04 03:16:19 giantbomb
    2012-10-17 02:36:20 day9tv
    2014-01-18 02:14:50 greenspeak
    2014-01-20 00:50:58 towelliee
    2014-07-16 05:42:50 camiwins
    2014-07-28 23:31:00 incontroltv
    ... <snip>


Rechat
------

Video objects can reprint chat, if the VOD is still available on twitch.tv .

::

    >>> for video in c.past_streams():
    ...     for chatline in video.chat_replay():
    ...         print "[%s] %s: %s" % (video.id, chatline['from'], chatline.message)
    ...         break
    ...     break
    ...
    [v80935574] mwthecool: Hey everyone!

TMI
---

``Channel`` method ``get_chatters`` can pull real-time chatters, moderators, and admins.

::

  >>> map(str, c.get_chatters().moderators)
  ['crosseye_jack', 'gray_mask', 'itmebot', 'itmejp', 'reginaldxiv', 'strippin', 'tahkai11', 'zodiacviii']


Caching
-------

Currently, only a file-based cache adapter is ready. Adapters for ``redis`` and ``memcached`` are planned for future releases.
To add a cache adapter, plug a ``CacheInterface`` compliant subclass directly to the ``itch.TwitchAPI`` before making requests.
The ``FileTreeCache`` accepts the optional environment variable ``TWITCH_CACHE_TEMP`` to set the cache path on disk.


::

    from cache.filetree import FileTreeCache
    from itch import TwitchAPI

    TwitchAPI.set_caching(FileTreeCache())


Todo
----

Focused on my own use-cases, kraken v3 resources are not completely covered.
This initial release of itch does not currently work with subscribers or subscriptions, games, or top stream lists.
