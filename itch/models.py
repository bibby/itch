import json
from itch import TwitchAPI as API
from itch import KRAKEN, RECHAT, TMI, MAX_GET, LOOTS, LOOTS_MAX_GET
from times import to_datetime
from log import logger
import re


class BaseModel(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            k = k.lstrip('_').replace('-', '_')
            self.__dict__.update({k: self.typeForKey(k, v)})

    def typeForKey(self, key, val):
        if key == 'links':
            val['own_url'] = val.pop("self")
            return Links(**val)

        if key in ('created_at', 'updated_at', 'recorded_at'):
            return to_datetime(val)

        return val

    def __repr__(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )

    def __getitem__(self, item):
        return self.__dict__.get(item)


class Links(BaseModel):
    pass


class Entity(BaseModel):
    def list_followers(self, direction=None, limit=None):
        direction = direction or 'ASC'
        req_limit = min(limit, MAX_GET)
        url = '{}/channels/{}/follows?direction={}&limit={}'
        url = url.format(KRAKEN, self.name, direction, req_limit)
        sent = 0
        for f in Entity.get_follows(url):
            yield Follow(**f)
            sent += 1
            if limit and sent >= limit:
                return

    def count_following(self):
        for f in self.list_following(limit=1):
            return f.total
        return 0

    def list_following(self, direction=None, limit=None):
        direction = direction or 'ASC'
        req_limit = min(limit, MAX_GET)
        url = '{}/users/{}/follows/channels?direction={}&limit={}'
        url = url.format(KRAKEN, self.name, direction, req_limit)
        sent = 0
        for f in Entity.get_follows(url):
            yield Follow(**f)
            sent += 1
            if limit and sent >= limit:
                return

    def live_stream(self):
        url = "{}/streams/{}"
        url = url.format(KRAKEN, self.name)
        res = API.get(url)
        stream = res.get("stream", None)
        if stream:
            return Stream(
                links=res.get("_links"),
                **stream
            )

    def past_streams(self, cap=None):
        url = "{}/channels/{}/videos"
        url = url.format(KRAKEN, self.name)
        params = {
            "broadcasts": "true",
        }

        read_count = 1
        vods_read = 0
        while read_count:
            if not url:
                return

            res = API.get(url, params)
            videos = res.get("videos", [])
            read_count = len(videos)
            for video in videos:
                yield Video(
                    total=res.get("_total"),
                    **video
                )

                vods_read += 1
                if cap and vods_read >= cap:
                    return
            url = res.get("_links").get("next", None)

    def loots_streams(self, limit=None, direction=None):
        url = "{}/search/channels/{}/streams"
        max_streams = LOOTS_MAX_GET
        direction = direction or 'desc'
        if limit:
            max_streams = min(limit, LOOTS_MAX_GET)

        params = {
            "json": json.dumps({
                "offset": 0,
                "limit": max_streams,
                "sort_key": "_t",
                "sort_order": direction.lower()
            })
        }

        url = url.format(LOOTS, self.id)
        res = API.get(url, params)
        for stream in res.get("data", []):
            yield LootsStream(**stream)

    @staticmethod
    def get_follows(url, cursor=None):
        payload = {}
        read_count = 1
        while read_count:
            if cursor:
                payload["cursor"] = cursor

            res = API.get(url, payload)
            if res:
                follows = res.get("follows", [])
                read_count = len(follows)
                for follow in follows:
                    follow['total'] = res.get('_total')
                    yield follow

                if read_count:
                    cursor = res.get("_cursor")
                    if not cursor:
                        url = res.get("_links").get("next")

    def get_chatters(self):
        url = "{}/group/user/{}/chatters"
        url = url.format(TMI, self.name)
        res = API.get(url)
        return Chatters(
            count=res.get("chatter_count"),
            **res.get("chatters")
        )


class Channel(Entity):
    @staticmethod
    def get(name):
        url = '{}/channels/{}'
        url = url.format(KRAKEN, name.lower().strip())
        return Channel(**API.get(url))

    def user(self):
        return User.get(self.name)


class User(Entity):
    @staticmethod
    def get(name):
        url = '{}/users/{}'
        url = url.format(KRAKEN, name.lower().strip())
        return User(**API.get(url))

    def channel(self):
        return Channel.get(self.name)


class Follow(BaseModel):
    type_classes = {
        'user': User,
        'channel': Channel,
    }

    def typeForKey(self, key, val):
        type_class = Follow.type_classes.get(key, None)
        if type_class:
            return type_class(**val)
        return BaseModel.typeForKey(self, key, val)


class Stream(BaseModel):
    def typeForKey(self, key, val):
        if key in ('preview'):
            return BaseModel(**val)
        return BaseModel.typeForKey(self, key, val)


class Video(BaseModel):
    @staticmethod
    def get(vid_id):
        url = '{}/videos/{}'
        url = url.format(KRAKEN, vid_id)
        return Video(**API.get(url))

    def typeForKey(self, key, val):
        if key in ('fps', 'resolutions'):
            return BaseModel(**val)

        if key == 'channel':
            return Channel(**val)

        if key == 'thumbnails':
            return [BaseModel(**t) for t in val]

        return BaseModel.typeForKey(self, key, val)

    def chat_replay(self):
        start, end = self._replay_boundaries()
        for message in self._replay_chat(start, end):
            yield ChatMessage(**message)

    def _replay_boundaries(self):
        payload = {
            "video_id": self.id,
            "start": 0,
        }

        res = API.get(RECHAT, payload)
        if "errors" not in res:
            raise Exception("Expected chat replay boundary error message.")

        msg = res.get("errors")[0].get("detail")
        mat = re.match('\d+ is not between (\d+) and (\d+)', msg)
        return tuple(map(int, [mat.group(1), mat.group(2)]))

    def _replay_chat(self, start, end):
        caches = [set(), set()]
        cache_index = 0
        while start <= end:
            prev_cache = caches[cache_index]
            cache_index = (cache_index + 1) % 2
            cache = caches[cache_index] = set()

            payload = {
                "video_id": self.id,
                "start": start,
            }

            res = API.get(RECHAT, payload)
            if "errors" in res:
                return

            for message in res.get("data"):
                mid = message.get("id")
                if mid in prev_cache:
                    continue

                cache.add(mid)
                yield message

            start += 30


class ChatMessage(BaseModel):
    def __init__(self, **kwargs):
        super(ChatMessage, self).__init__(**kwargs)
        super(ChatMessage, self).__init__(**{
            'from': self.attributes['from'],
            'message': self.attributes.message,
            'subscriber': self.attributes.tags.subscriber,
        })

    @staticmethod
    def get(id):
        url = '{}/rechat-message/{}'
        url = url.format(RECHAT, id)
        return ChatMessage(**API.get(url))

    def typeForKey(self, key, val):
        if key == 'attributes':
            return ChatMessageAttributes(**val)
        return BaseModel.typeForKey(self, key, val)


class ChatMessageAttributes(BaseModel):
    def typeForKey(self, key, val):
        if key == 'tags':
            return ChatMessageTags(**val)
        return BaseModel.typeForKey(self, key, val)


class ChatMessageTags(BaseModel):
    pass


class Chatters(BaseModel):
    pass


class LootsStream(BaseModel):
    # TODO
    pass