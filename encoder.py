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
        self.A     = np.uint32(0x10000)
        self.C     = np.uint32(0)
        self.CT    = 11
        self.ST    = 0
        self.Bx    = None
        self.B     = None

        # temporary attributes for byte_out()
        self.BPST = 0
        self.BP   = self.BPST - 1
        self.ST   = 0

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

    def code_lps(self):
        self.A -= self.Qe
        if not self.A < self.Qe:
            self.C += self.A
            self.A = self.C
        self.estimate_Qe_after_lps()
        self.renorm_e()

    def estimate_Qe_after_lps(self):
        if self.table.is_exchange_needed:
            self.MPS = 1 - self.MPS
        self.update_using_lps()

    def code_mps(self):
        self.A -= self.Qe
        if not self.A < self.threequarter:
            return
        if self.A < self.Qe:
            self.C += self.A
            self.A = self.C
        self.estimate_Qe_after_mps()
        self.renorm_e()

    def estimate_Qe_after_mps():
        self.table.update_using_mps()

    def renorm_e(self):
        self.A = np.left_shift(self.A, 1)
        self.C = np.left_shift(self.C, 1)
        self.CT -= 1
        if self.CT == 0:
            self.byte_out()
            self.CT = 8
        if self.A < self.threequarter:
            self.renorm_e()

    def byte_out(self):
        T = np.right_shift(self.C, 19)
        if T > 0xFF:
            self.B += 1
            self.stuff_0()
            self.output_stacked_zeros()
            self.BP += 1
            self.B = T
        if not T == 0xFF:
            self.output_stacked_xffs()
            self.BP += 1
            self.B = T
        else:
            self.ST += 1
        self.C = np.bitwise_and(self.C, 0x7FFFF)

    def stuff_0(self):
        if self.B == 0xFF:
            self.BP += 1
            self.B = 0

    def output_stacked_zeros(self):
        while self.ST != 0:
            self.BP += 1   # current location of output byte?
            self.B = 0     # this should be written on disk?
            self.ST -= 1

    def output_stacked_xffs(self):
        while self.ST != 0:
            self.BP += 1
            self.B = 0xFF  # this should be written on disk?
            self.BP += 1
            self.B = 0     # this should be written on disk?
            self.ST -= 1

    def flush(self):
        self.clear_final_bits()
        self.C = np.left_shift(self.C, self.CT)
        self.byte_out()
        self.C = np.left_shift(self.C, 8)
        self.byte_out()
        self.discard_final_zeros()

    def clear_final_bits(self):
        T = self.C + self.A - 1
        T = np.bitwise_and(self.T, 0xFFFF0000)
        if T < self.C:
            T += self.threequarter
        self.C = T

    def discard_final_zeros(self):
        if self.BP < self.BPST:
            return
        if self.B == 0:
            self.BP -= 1
            self.discard_final_zeros()
        if self.B == 0xFF:
            self.BP += 1
