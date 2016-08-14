import argparse
import sys
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from collections import namedtuple
from datetime import datetime
from itch.times import to_datetime, to_timestamp
from itch.log import logger
import matplotlib.colors as mcolors


headers = [
    'name',
    'channel',
    'created',
    'followed',
    'delta',
    'followers',
    'following',
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


def make_colormap(seq):
    """Return a LinearSegmentedColormap
    seq: a sequence of floats and RGB-tuples. The floats should be increasing
    and in the interval (0,1).
    """
    seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]
    cdict = {'red': [], 'green': [], 'blue': []}
    for i, item in enumerate(seq):
        if isinstance(item, float):
            r1, g1, b1 = seq[i - 1]
            r2, g2, b2 = seq[i + 1]
            cdict['red'].append([item, r1, r2])
            cdict['green'].append([item, g1, g2])
            cdict['blue'].append([item, b1, b2])
    return mcolors.LinearSegmentedColormap('CustomMap', cdict)


def read_file(infile, delimiter):
    with open(infile, 'r') as csv:
        for k, line in enumerate(csv.readlines()):
            lp = line.strip().split(delimiter)
            rec = lp[:len(headers)]
            rec += record_defaults[len(rec):]
            yield Record(*tuple(rec))


def colorize_axis(ax, font_color):
    ax.yaxis.label.set_color(font_color)
    ax.xaxis.label.set_color(font_color)
    ax.spines['bottom'].set_color(font_color)
    ax.spines['top'].set_color(font_color)
    ax.spines['right'].set_color(font_color)
    ax.spines['left'].set_color(font_color)

    ax.tick_params(axis='x', colors=font_color, which='both')
    ax.tick_params(axis='y', colors=font_color, which='both')


def graph(args):

    if args.xmin:
        args.xmin = types.get(args.xfield, int)(args.xmin)

    if args.xmax:
        args.xmax = types.get(args.xfield, int)(args.xmax)

    if args.ymin:
        args.ymin = types.get(args.yfield, int)(args.ymin)

    if args.ymax:
        args.ymax = types.get(args.yfield, int)(args.ymax)

    x = []
    y = []
    l = []
    li = 0
    font_color = (0.7, 0.7, 0.7, 1.0)
    bg_color = (0.05, 0.05, 0.05)

    logger.info('Gathering data..')
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
        x.append(xval)
        y.append(yval)
        l.append(li)

    logger.info("Items: %d", len(l))
    logger.info('Setting up plot..')

    line_fill_color = 'y'
    line_fill_alpha = 0.03
    xtype = types.get(args.xfield, int)
    ytype = types.get(args.yfield, int)

    scatter_ax = None
    line_ax = None
    if args.type in ['scatter', 'mixed']:

        dot_size = 5
        c = mcolors.ColorConverter().to_rgb
        cmap = make_colormap([
            c('blue'),
            c('indigo'),
            c('purple'),
            c('magenta'),
            c('red')
        ])

        logger.info('Scatter config..')
        fig, scatter_ax = plt.subplots()
        fig.patch.set_facecolor(bg_color)

        scatter_ax.grid(True, color=font_color)
        scatter_ax.set_axis_bgcolor(bg_color)
        scatter_ax.set_ylabel(args.yfield)
        scatter_ax.set_xlabel(args.label or args.xfield)

        colorize_axis(scatter_ax, font_color)

        logger.info('Calculate the point density..')
        xx = x
        if xtype == _dt:
            xx = [to_timestamp(xv) for xv in x]

        yy = y
        if ytype == _dt:
            yy = [to_timestamp(yv) for yv in y]

        xy = np.vstack([xx, yy])
        z = gaussian_kde(xy)(xy)

        logger.info('Drawing scatter..')
        plt.scatter(x, y, c=z, s=dot_size, edgecolor='', cmap=cmap)
        if types.get(args.yfield, int) == int:
            scatter_ax.set_ylim(ymin=args.ymin or 0, ymax=args.ymax)

    if args.type in ['line', 'mixed']:
        logger.info('Setting up line chart..')
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
        line_ax.set_ylabel('count', rotation=line_ylabel_rot, labelpad=20)
        colorize_axis(line_ax, font_color)

        logger.info('Drawing line chart..')
        plt.plot(x, l, line_fill_color)
        line_ax.fill_between(
            x,
            l,
            facecolor=line_fill_color,
            alpha=line_fill_alpha
        )

    logger.info('Limits and ticks..')
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
        plt.title(args.title, color=font_color)

    logger.info('Rendering figure: %s', args.outfile)

    fig.set_size_inches(12, 6)
    plt.savefig(
        args.outfile,
        facecolor=fig.get_facecolor(),
        edgecolor='none',
        bbox_inches='tight',
        dpi=180
    )


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
