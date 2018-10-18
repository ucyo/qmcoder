#!/usr/bin/env python
# coding: utf-8
"""
Pre-computed probability tables.
"""
import pandas as pd
import os

_bf = os.path.dirname(__file__)

JPEG_TABLE = pd.read_csv(os.path.join(_bf, 'jpeg.csv'), index_col=0,
                        converters={'qe':lambda x: int(x, 16), 'exmps': lambda x: bool(int(x))},
                        dtype={x:'uint8' for x in ['ix', 'nlps', 'nmps']}
                        )

ILLUSTRIVE_TABLE = pd.read_csv(os.path.join(_bf, 'illustrative.csv'), index_col=0,
                               converters={'qe':lambda x: int(x, 16), 'exmps': lambda x: bool(int(x))},
                               dtype={x:'int8' for x in ['ix', 'nlps', 'nmps']}
                               )


class JPEGProbabilityTable(object):

    def __init__(self):
        self.table = JPEG_TABLE
        self.index = 0

    @property
    def one(self):
        return 0xB55A

    @property
    def threequarter(self):
        return int((self.one//(4/3))+1)

    @property
    def half(self):
        return self.one//2+1

    @property
    def qe(self):
        return self.table['qe'][self.index]

    def update_mps(self):
        self.index = self.table['nmps'][self.index]

    def update_lps(self):
        self.index = self.table['nlps'][self.index]

    @property
    def is_exchange_needed(self):
        return self.table['exmps'][self.index]


class IllustrativeProbabilityTable(object):

    def __init__(self):
        self.table = ILLUSTRIVE_TABLE
        self.index = 0

    @property
    def one(self):
        return 0xAAAA

    @property
    def threequarter(self):
        return int((self.one//(4/3))+1)

    @property
    def half(self):
        return self.one//2+1

    @property
    def qe(self):
        return self.table['qe'][self.index]

    def update_mps(self):
        self.index += self.table['nmps'][self.index]

    def update_lps(self):
        self.index += self.table['nlps'][self.index]

    @property
    def is_exchange_needed(self):
        return self.table['exmps'][self.index]