import sys
import argparse
from itch.reports import reports


def main():
    args = __parse_args()
    report = reports.get(args.command)
    report(**vars(args))


def __parse_args():
    args = argparse.ArgumentParser(description='Twitch.tv APIs module')
    args.add_argument(
        'command',
        nargs='?',
        help='command',
        choices=reports.keys(),
    )

    args.add_argument(
        'channel',
        nargs='?',
        help='channel',
    )

    args.add_argument(
        '-d', '--direction',
        dest='direction',
        help='sorting direction',
        choices=['asc', 'desc']
    )

    args.add_argument(
        '-l', '--limit',
        dest='limit',
        help='number of items to pull',
        type=int
    )

    args.add_argument(
        '-c', '--cache',
        dest='caching',
        help='cache type. See README for required env vars',
        choices=['file', 'redis', 'memcache']
    )

    options = args.parse_args(sys.argv[1:])
    if not options.command and not options.version:
        args.print_help()
        exit()
    return options
