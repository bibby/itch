import argparse
import sys
import re
import matplotlib.pyplot as plt
from collections import namedtuple
from datetime import datetime
from itch.times import to_datetime
from itch.log import logger


headers = [
    'name',
    'channel',
    'created',
    'followed',
    'delta',
    'followers',
    'following'
]

record_defaults = [
    'undefined',
    'undefined',
    '0000-00-00',
    '0000-00-00',
    0,
    0,
    0
]


def _dt(t):
    if re.match('\d+-\d+-\d+', t):
        return to_datetime(t)
    return datetime.utcfromtimestamp(float(t)).replace(tzinfo=None)

types = {
    'created': _dt,
    'followed': _dt,
    'name': str,
    'channel': str,
}

Record = namedtuple('Record', headers)


def value(record, attr):
    val = getattr(record, attr)
    typ = types.get(attr, int)
    return typ(val)


def main():
    args = __parse_args()
    graph(args)


def __parse_args(arg_string=None):
    args = argparse.ArgumentParser(description='plot generator')

    args.add_argument(
        '-x',
        dest='xfield',
        action='store',
        help='X axis field name',
        default='followed',
    )

    args.add_argument(
        '-y',
        dest='yfield',
        action='store',
        help='Y axis field name',
        default='created',
    )

    args.add_argument(
        '-m', '--xmin',
        dest='xmin',
        action='store',
        help='min x value',
    )

    args.add_argument(
        '-M', '--xmax',
        dest='xmax',
        action='store',
        help='maz x value',
    )

    args.add_argument(
        '-n', '--ymin',
        dest='ymin',
        action='store',
        help='yin x value',
    )

    args.add_argument(
        '-N', '--ymax',
        dest='ymax',
        action='store',
        help='max y value',
    )

    args.add_argument(
        '-d', '--delimiter',
        dest='delimiter',
        action='store',
        help='field delimiter',
        default="\t",
    )

    args.add_argument(
        '-r', '--record',
        dest='record',
        action='store_true',
        help='print whole record (for saving subsets)',
        default=False,
    )

    args.add_argument(
        '-s', '--silent',
        dest='silent',
        action='store_true',
        help='skip printouts',
        default=False,
    )

    args.add_argument(
        '-Y', '--summary',
        dest='summary',
        action='store_true',
        help='print a summary',
        default=False,
    )

    args.add_argument(
        '-S', '--streams',
        dest='streams',
        action='store',
        help='streams json',
        default=None,
    )

    args.add_argument(
        '-t', '--type',
        dest='type',
        action='store',
        help='graph type',
        default='mixed',
        choices=['scatter', 'line', 'mixed']
    )

    args.add_argument(
        '-l', '--label',
        dest='label',
        action='store',
        help='x label',
    )

    args.add_argument(
        '-T', '--title',
        dest='title',
        action='store',
        help='chart title',
    )

    args.add_argument(
        'infile',
        nargs='?',
        action='store',
        help='InFile',
    )

    args.add_argument(
        'outfile',
        nargs='?',
        action='store',
        help='OutFile',
        default='/tmp/plot.png',
    )

    options = args.parse_args(arg_string or sys.argv[1:])
    if not options.infile:
        args.print_help()
        exit()
    return options


def read_file(infile, delimiter):
    with open(infile, 'r') as csv:
        for k, line in enumerate(csv.readlines()):
            lp = line.strip().split(delimiter)
            rec = lp[:len(headers)]
            rec += record_defaults[len(rec):]
            yield Record(*tuple(rec))


def graph(args):

    if args.xmin:
        args.xmin = types.get(args.xfield, int)(args.xmin)

    if args.xmax:
        args.xmax = types.get(args.xfield, int)(args.xmax)

    if args.ymin:
        args.ymin = types.get(args.yfield, int)(args.ymin)

    if args.ymax:
        args.ymax = types.get(args.yfield, int)(args.ymax)

    points = set()
    li = 0

    for record in read_file(args.infile, args.delimiter):
        xval = value(record, args.xfield)
        if args.xmin and args.xmin > xval:
            continue
        if args.xmax and args.xmax < xval:
            continue

        yval = value(record, args.yfield)
        if args.ymin and args.ymin > yval:
            continue

        if args.ymax and args.ymax < yval:
            continue

        if not args.silent:
            if args.record:
                print args.delimiter.join(map(str, tuple(record)))
            else:
                print xval, yval, record.name

        li += 1
        points.add((xval, yval, li))

    if args.summary:
        print "Items: %d" % (len(points),)

    l = []
    x = []
    y = []
    line_fill_color = 'r'

    for xp, yp, lp in points:
        x.append(xp)
        y.append(yp)
        l.append(lp)

    scatter_ax = None
    line_ax = None
    if args.type in ['scatter', 'mixed']:
        fig, scatter_ax = plt.subplots()
        scatter_ax.grid(True)
        scatter_ax.set_ylabel(args.yfield)
        scatter_ax.set_xlabel(args.label or args.xfield)
        plt.scatter(x, y, s=10)
        if types.get(args.yfield, int) == int:
            scatter_ax.set_ylim(ymin=args.ymin or 0, ymax=args.ymax)

    if args.type in ['line', 'mixed']:
        if scatter_ax:
            line_ax = scatter_ax.twinx()
            line_ylabel_rot = 270
        else:
            line_ax.set_xlabel(args.label or args.xfield)
            fig, line_ax = plt.subplots()
            line_ylabel_rot = None
            line_ax.grid(True)
        x = sorted(x)
        l = sorted(l)
        line_ax.set_ylabel('count', rotation=line_ylabel_rot)
        plt.plot(x, l, line_fill_color)
        line_ax.fill_between(x, l, facecolor=line_fill_color, alpha=0.33)


    xtype = types.get(args.xfield, int)
    if args.xmin:
        plt.xlim(xmin=args.xmin or 0, xmax=args.xmax)

    if xtype == _dt:
        for ax in fig.axes:
            plt.sca(ax)
            plt.xticks(rotation=33)
        if args.streams:
            plot_streams(args.streams, min(x), max(x))

    if types.get(args.yfield, int) == int and args.type != 'line':
        plt.ylim(ymin=args.ymin or 0, ymax=args.ymax)

    if args.title:
        plt.title(args.title)

    logger.info('Rendering figure: %s', args.outfile)
    plt.savefig(args.outfile, bbox_inches='tight')


def plot_streams(streams_src, minx, maxx):
    stream_fill_color = 'g'
    with open(streams_src, 'r') as streams:
        for line in streams.readlines():
            start, end = tuple(line.strip().split("\t"))
            start = _dt(start)
            end = _dt(end)

            if minx > end:
                continue
            if maxx < start:
                continue

            plt.axvspan(
                start,
                end,
                facecolor=stream_fill_color,
                alpha=0.5
            )

if __name__ == '__main__':
    main()
