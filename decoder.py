#!/usr/bin/env python
# coding: utf-8
"""
Decoder class
"""
import numpy as np

class Decoder(object):

    def __init__(self, table):
        self.table = table
        self.C     = np.uint32(0x0)
        self.A     = np.uint32(0x10000)

    @property
    def Qe(self):
        return np.uint16(self.table.qe)

    @property
    def Cx(self):
        return np.bitwise_and(self.C, 0xFFFF0000)

    @property
    def Clow(self):
        return np.bitwise_and(self.C, 0x0000FFFF)