#!/usr/bin/env python
# coding: utf-8
"""
Encoder class
"""
import numpy as np

class Encoder(object):

    def __init__(self, probTable):
        self.table = probTable
        self.EC    = 0
        self.D     = None
        self.MPS   = 0
        self.CX    = None
        self.A     = np.uint32(0)
        self.C     = np.uint32(0)
        self.CT    = 11
        self.ST    = 0
        self.Bx    = None
        self.B     = None

    @property
    def Qe(self):
        return np.uint32(self.table.qe)

    @property
    def one(self):
        return np.uint32(self.table.one)

    @property
    def threequarter(self):
        return np.uint32(self.table.threequarter)

    @property
    def half(self):
        return np.uint32(self.table.half)

    def encode(value):
        if value == self.MPS:
            self.code_mps()
        else:
            self.code_lps()