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