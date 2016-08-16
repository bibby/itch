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
Cache keys are the ``sha256`` of URLs with query parameters, and the values are compressed responses.
To add a cache adapter, plug a ``CacheInterface`` compliant subclass directly to the ``itch.TwitchAPI`` before making requests.

::

    from cache.filetree import FileTreeCache
    from itch import TwitchAPI

    TwitchAPI.set_caching(FileTreeCache())


FileTreeCache
~~~~~~~~~~~~~

The ``FileTreeCache`` accepts the optional environment variable ``TWITCH_CACHE_TEMP`` to set the cache path on disk.


RedisCache
~~~~~~~~~~

``rcache.RedisCache`` requires the pip module ``redis``, which is not installed by itch. Starting with itch 0.3, the required modules can be installed by pip installing ``itch[cache]`` or ``itch[complete]``.
This cache makes use the following environment variables:

::

    REDIS_HOST (default: localhost)
    REDIS_PORT (default: 6379)
    REDIS_PASSWORD (default: '')
    REDIS_DB (default: 1)


MemcacheCache
~~~~~~~~~~~~~

``mcache.MemcacheCache`` requires the pip module ``python-memcached``, which is not installed by itch.
This cache makes use the ``MEMCACHE_SERVERS`` environment variable, which should be a comma separated list
of ``<host>:<port>`` items. The default value is ``127.0.0.1:11211``.

Starting with itch 0.3, the required modules can be installed by pip installing ``itch[cache]`` or ``itch[complete]``.


CLI
---

The command line tool prints tab-separated reports that are suitable for the plotter.

::

    $ itch -h
    usage: itch [-h] [-d {asc,desc}] [-l LIMIT] [-c {file,redis,memcache}]
                [{chatlog,created,chatters,num_following,num_followers,followers,following,loots_streams}]
                [channel]

    Twitch.tv APIs module

    positional arguments:
      {chatlog,created,chatters,num_following,num_followers,followers,following,loots_streams}
                            command
      channel               channel

    optional arguments:
      -h, --help            show this help message and exit
      -d {asc,desc}, --direction {asc,desc}
                            sorting direction
      -l LIMIT, --limit LIMIT
                            number of items to pull
      -c {file,redis,memcache}, --cache {file,redis,memcache}
                            cache type. See README for required env vars
Plotter
-------

The cli tool ``itch-plot`` renders charts with data extracted from the ``itch`` CLI or other custom tools. The
module requires the pip modules ``matplotlib`` and ``scipy``, which is not installed by itch (because ``numpy``).

Starting with itch 0.3, the required modules can be installed by pip installing ``itch[plot]`` or ``itch[complete]``.

::

    $ itch-plot -h
    usage: itch-plot [-h] [-x XFIELD] [-y YFIELD] [-m XMIN] [-M XMAX] [-n YMIN]
                     [-N YMAX] [-d DELIMITER] [-r] [-s] [-S STREAMS]
                     [-t {scatter,line,mixed}] [-l LABEL] [-T TITLE] [-D]
                     [infile] [outfile]

    plot generator

    positional arguments:
      infile                InFile
      outfile               OutFile

    optional arguments:
      -h, --help            show this help message and exit
      -x XFIELD             X axis field name
      -y YFIELD             Y axis field name
      -m XMIN, --xmin XMIN  min x value
      -M XMAX, --xmax XMAX  maz x value
      -n YMIN, --ymin YMIN  yin x value
      -N YMAX, --ymax YMAX  max y value
      -d DELIMITER, --delimiter DELIMITER
                            field delimiter
      -r, --record          print whole record (for saving subsets)
      -s, --silent          skip printouts
      -S STREAMS, --streams STREAMS
                            streams json
      -t {scatter,line,mixed}, --type {scatter,line,mixed}
                            graph type
      -l LABEL, --label LABEL
                            x label
      -T TITLE, --title TITLE
                            chart title
      -D, --density         Density coloration; much slower renders


Example data pull and chart render:

::

    # dump the last 1K followers to a file
    itch -l 1000 -c file followers burkeblack > followers.csv

    # dump the last 20 streams to a file
    itch -l 20 -c file loots_streams burkeblack > streams.csv

    # plot the followers while overlaying the streams,
    # trimming the viewport and setting a title.
    itch-plot -sS streams.csv -m '2016-07-25' -M '2016-08-01' \
    -T 'BurkeBlack - last 1K' followers.csv plot.png

Here is the `resulting graph <https://scannersweep.com/misc/4e5f315e76ceac2f256a28c53b8144ea.png>`_


Todo
----

Focused on my own use-cases, kraken v3 resources are not completely covered.
This initial release of itch does not currently work with subscribers or subscriptions, games, or top stream lists.
