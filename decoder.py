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
        self.BPST  = 0
        self.BP    = self.BPST - 1

        self.byte_in()
        self.C = np.left_shift(self.C, 8)
        self.byte_in()
        self.C = np.left_shift(self.C, 8)
        self.CT = 0
        self.B = 0


    @property
    def Qe(self):
        return np.uint16(self.table.qe)

    @property
    def Cx(self):
        return np.bitwise_and(self.C, 0xFFFF0000)

    @property
    def Clow(self):
        return np.bitwise_and(self.C, 0x0000FFFF)

    def byte_in(self):
        self.BP += 1
        if self.B == 0xFF:
            self.unstuff_0()
        else:
            self.C += np.left_shift(self.B, 8)

    def unstuff_0(self):
        self.BP += 1
        if self.B == 0:
            self.C = np.logical_or(C, 0xFF00)
        else:
            # (interpret marker)
            # Adjust BP
            # write zeros until end of decoding