from datetime import datetime
from dateutil.parser import parse as dateparse


def to_datetime(date_string):
    if isinstance(date_string, (datetime,)):
        return date_string

    if isinstance(date_string, (int,)):
        return datetime.utcfromtimestamp(date_string)

    return dateparse(date_string).replace(tzinfo=None)


def to_timestamp(dt):
    epoch = datetime(1970, 1, 1).replace(tzinfo=None)
    if not isinstance(dt, (datetime, )):
        dt = to_datetime(dt)
    return int((dt - epoch).total_seconds())


def subtime(a, b):
    return to_timestamp(b) - to_timestamp(a)
