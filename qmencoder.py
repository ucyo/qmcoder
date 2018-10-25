#!/usr/bin/env python
# coding: utf-8
"""
QM-Encoder.

This is a Python implementation of the QM-Encoder.

Usage:
  qmencoder.py (-c|-d) IN [OUT] [--table=<table>]
  qmencoder.py -h | --help
  qmencoder.py --version

Options:
  -h --help        Show this screen
  -v --version     Show version
  --table=<table>  Table selection [default: jpeg]
  -c --compress    compress file
  -d --decompress  decompress file
"""

from docopt import docopt
from functools import namedtuple as nt
from decoder import Decoder, decompress
from encoder import Encoder, compress
from tables import lookuptable
from functools import namedtuple as nt


def parse_arg(arg):
    ARG = nt('Arguments', 'fname, oname, table, compress')

    if arg['--table'] not in lookuptable.keys():
        msg = "Wrong lookup table"
        raise Exception(msg)
    if arg['OUT'] is None:
        arg['OUT'] = arg['IN']
        if arg['--compress']:
            arg['OUT'] += '.qmenc'
        else:
            arg['OUT'] += '.recon'
    oname = arg['OUT']
    table = arg['--table']
    fname = arg['IN']
    compress = arg['--compress']
    return ARG(fname, oname, table, compress)


if __name__ == '__main__':
    arg = docopt(__doc__, version="0.1")
    print(arg)
    arg = parse_arg(arg)

    if arg.compress:
        compress(arg.fname, arg.oname, arg.table)
    else:  # decompress
        decompress(arg.fname, arg.oname, arg.table)
