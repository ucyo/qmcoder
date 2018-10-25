#!/usr/bin/env python
# coding: utf-8
"""
Decoder class
"""
import numpy as np
import bitstring as bs
from tables import lookuptable
import logging


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
        self.out   = bs.BitArray()
        self.initialization()
        self.logger = logging.getLogger(__name__)

    def initialization(self):
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
        return np.right_shift(self.C, 16)

    @property
    def Clow(self):
        return np.bitwise_and(self.C, 0x0000FFFF)

    @property
    def one(self):
        return np.uint16(self.table.one)

    @property
    def threequarter(self):
        return np.uint16(self.table.threequarter)

    @property
    def half(self):
        return np.uint16(self.table.half)

    def byte_in(self):
        self.BP += 1
        self.B = self.file[0]; self.file = self.file[1:]
        if self.B == 0xFF:
            self.unstuff_0()
        else:
            self.C += np.left_shift(self.B, 8)

    def unstuff_0(self):
        self.BP += 1
        self.B = self.file[0]; self.file = self.file[1:]
        if self.B == 0:
            self.C = np.bitwise_or(self.C, 0xff00)
        else:
            pass
            # Marker found;
            # Adjust BP and
            # write zeros until end of decoding

    def decode(self):
        self.EC += 1
        self.A -= self.Qe
        self.logger.debug(str(self))
        if not self.Cx < self.A:
            D = self.cond_LPS_exchange()
            self.renorm_d()
            self.out.append(bin(D))
            return
        if self.A < self.threequarter:
            D = self.cond_MPS_exchange()
            self.renorm_d()
            self.out.append(bin(D))
        else:
            D = self.MPS
            self.out.append(bin(D))

    def cond_LPS_exchange(self):
        if self.A < self.Qe:
            D = self.MPS
            self.C -= np.left_shift(self.A, 16)
            self.A = self.Qe
            self.estimate_qe_after_mps()
        else:
            D = 1 - self.MPS
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
        str_B = "0x{}".format(hex(self.B)[2:].zfill(2).upper()) if self.B else self.B
        result = [self.EC, self.D, self.MPS, self.table.is_exchange_needed,
                  "0x{}".format(hex(self.Qe)[2:].zfill(5).upper()),
                  "0x{}".format(hex(self.A)[2:].zfill(5).upper()),
                  "0x{}".format(hex(self.C)[2:].zfill(8).upper()),
                  self.CT, str_B
                  ]

        result = "\t".join([str(x) for x in result])
        return result


def decompress(fname, oname, table):

    ptable = lookuptable[table]

    # read compressed file and initialise decompressor
    with open(fname, 'rb') as f:
        expected = f.read()
        dec = Decoder(ptable(), expected)

    # reconstruct input from compressed file in memory
    for val in range(len(expected)*8):
        dec.decode()

    # write reconstructed file to disk
    with open(oname, 'wb') as f:
        dec.out.tofile(f)


if __name__ == "__main__":

    fname = './tests/test.raw.compressed'
    oname = './tests/test.raw.qmrecon'

    decompress(fname, oname, 'jpeg')