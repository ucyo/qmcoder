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
        self.MPS   = 0

        self.byte_in()
        self.C = np.left_shift(self.C, 8)
        self.byte_in()
        self.C = np.left_shift(self.C, 8)
        self.CT = 0
        self.B = 0


    @property
    def Qe(self):
        return np.uint32(self.table.qe)

    @property
    def Cx(self):
        return np.bitwise_and(self.C, 0xFFFF0000)

    @property
    def Clow(self):
        return np.bitwise_and(self.C, 0x0000FFFF)

    @property
    def one(self):
        return np.uint32(self.table.one)

    @property
    def threequarter(self):
        return np.uint32(self.table.threequarter)

    @property
    def half(self):
        return np.uint32(self.table.half)

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

    def decode(self):
        self.A -= self.Qe
        if not self.A < self.Cx:
            D = self.cond_LPS_exchange()
            self.renorm_d()
            return
        if self.A < self.threequarter:
            D = self.cond_MPS_exchange()
            self.renorm_d()
        else:
            D = self.MPS
        return D

    def cond_LPS_exchange(self):
        if self.A < self.Qe:
            D = self.MPS
            # self.Cx -= self.A
            self.C -= np.left_shift(self.A, 16)
            self.A = self.Qe
            self.estimate_qe_after_mps()
        else:
            D = 1 - self.MPS
            # self.Cx -= self.A
            self.C -= np.left_shift(self.A, 16)
            self.A = self.Qe
            self.estimate_qe_after_lps()
        return D

    def cond_MPS_exchange(self):
        if self.A < self.Qe:
            D = 1 - self.MPS
            self.estimate_qe_after_lps()
        else:
            D = self.MPS
            self.estimate_qe_after_mps()
        return D

    def renorm_d(self):
        if self.CT == 0:
            self.byte_in()
            self.CT = 8
        self.A = np.left_shift(self.A, 1)
        self.C = np.left_shift(self.C, 1)
        self.CT -= 1
        if self.A < self.threequarter:
            self.renorm_d()

    def estimate_qe_after_lps(self):
        if self.table.is_exchange_needed:
            self.MPS = 1 - self.MPS
        self.table.update_using_lps()

    def estimate_qe_after_mps(self):
        self.table.update_using_mps()
