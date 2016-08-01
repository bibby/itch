import sys
import argparse


def __cli_main():
    import reports

    reports = dict(
        followers=reports.print_followers,
        following=reports.print_following,
        loots_streams=reports.loots_streams
    )

    args = __parse_args()
    report = reports.get(args.command)
    report(**vars(args))


def __parse_args():
    args = argparse.ArgumentParser(description='Twitch.tv APIs module')
    args.add_argument(
        'command',
        nargs='?',
        help='command',
        choices=['followers', 'following', 'loots_streams'],
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
