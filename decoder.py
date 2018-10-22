#!/usr/bin/env python
# coding: utf-8
"""
Decoder class
"""
import numpy as np

class Decoder(object):

    def __init__(self, table, file):
        self.table = table
        self.file  = file
        self.C     = np.uint32(0x0)
        self.A     = np.uint32(0x10000)
        self.BPST  = 0
        self.BP    = self.BPST - 1
        self.MPS   = 0
        self.EC    = 1
        self.D     = 0
        self.initialization()

    def initialization(self):
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
        self.B = self.file[0]; self.file = self.file[1:]
        if self.B == 0xFF:
            self.unstuff_0()
        else:
            self.C += np.left_shift(self.B, 8)

    def unstuff_0(self):
        self.BP += 1
        if self.B == 0:
            self.C = np.logical_or(self.C, 0xFF00)
        else:
            pass# (interpret marker)
            # Adjust BP
            # write zeros until end of decoding

    def decode(self):
        self.EC += 1
        self.A -= self.Qe
        if not self.Cx < self.A:
            D = self.cond_LPS_exchange()
            self.renorm_d()
            return D
        if self.A < self.threequarter:
            D = self.cond_MPS_exchange()
            self.renorm_d()
            return D
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

    def __repr__(self):
        str_B = "0x{}".format(hex(self.B)[2:].zfill(2).upper()) if self.B else None
        result = [self.EC, self.D, self.MPS, self.table.is_exchange_needed,
                  "0x{}".format(hex(self.Qe)[2:].zfill(5).upper()),
                  "0x{}".format(hex(self.A)[2:].zfill(5).upper()),
                  "0x{}".format(hex(self.C)[2:].zfill(8).upper()),
                  self.CT, str_B
                  ]

        result = "\t".join([str(x) for x in result])
        return result

if __name__ == "__main__":
    import sys
    from tests import expected
    from tables import JPEGProbabilityTable

    ptable = JPEGProbabilityTable()
    dec = Decoder(ptable, expected)

    print("\t".join(["EC","D","MPS","CX","{:7}".format("Qe"),
                     "{:7}".format("A"),"{:8}".format("C"),"CT","B"]))
    for val in range(int(sys.argv[1])):
        print(dec)
        v = dec.decode()
        # print(v)