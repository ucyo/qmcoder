#!/usr/bin/env python
# coding: utf-8
"""
Encoder class
"""
import numpy as np
import bitstring as bs
from tables import lookuptable

class Encoder(object):

    def __init__(self, probTable):
        self.table = probTable
        self.EC    = 1
        self.D     = 0
        self.MPS   = 0
        self.CX    = None
        self.A     = np.uint32(0x10000)
        self.C     = np.uint32(0)
        self.CT    = 11
        self.ST    = 0
        self.Bx    = False
        self.B     = None

        # temporary attributes for byte_out()
        self.BPST = 0
        self.BP   = self.BPST - 1
        self.ST   = 0

        self.out = bs.BitArray()

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

    def encode(self, value):
        if value == self.MPS:
            self.code_mps()
        else:
            self.code_lps()
        self.EC += 1    # for printing purposes
        self.D = value  # for printing purposes

    def code_lps(self):
        self.A -= self.Qe
        if not self.A < self.Qe:
            self.C += self.A
            self.A = self.Qe
        self.estimate_Qe_after_lps()
        self.renorm_e()

    def estimate_Qe_after_lps(self):
        if self.table.is_exchange_needed:
            self.MPS = 1 - self.MPS
        self.table.update_using_lps()

    def code_mps(self):
        self.A -= self.Qe
        if not self.A < self.threequarter:
            return
        if self.A < self.Qe:
            self.C += self.A
            self.A = self.Qe
        self.estimate_Qe_after_mps()
        self.renorm_e()

    def estimate_Qe_after_mps(self):
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
            self.Bx = True
        if not T == 0xFF:
            self.output_stacked_xffs()
            self.BP += 1
            self.B = T

            # Not according to Standard
            if self.B != 0 and not self.Bx:
                self.out.append(hex(self.B))
            if self.B != 0 and self.Bx:
                last_entry = int(self.out[-8:].bin, 2)
                self.out = self.out[:-8]
                self.out.append(hex(last_entry+1))
                self.out.append(bs.BitString(uint=0, length=8))
            self.Bx = False
        else:
            self.ST += 1
        self.C = np.bitwise_and(self.C, 0x7FFFF)

    def stuff_0(self):
        if self.B == 0xFF:
            self.BP += 1
            self.B = 0
            self.out.append(hex(self.B))


    def output_stacked_zeros(self):
        while self.ST != 0:
            self.BP += 1
            self.B = 0
            self.out.append(hex(self.B))
            self.ST -= 1


    def output_stacked_xffs(self):
        while self.ST != 0:
            self.BP += 1
            self.B = 0xFF
            self.out.append(hex(self.B))
            self.BP += 1
            self.B = 0
            self.out.append(bs.BitString(uint=0, length=8))
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
        T = np.bitwise_and(T, 0xFFFF0000)
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

    def __repr__(self):
        str_B = "0x{}".format(hex(self.B)[2:].zfill(2).upper()) if self.B else None
        result = [self.EC, self.D, self.MPS, self.table.is_exchange_needed,
                  "0x{}".format(hex(self.Qe)[2:].zfill(5).upper()),
                  "0x{}".format(hex(self.A)[2:].zfill(5).upper()),
                  "0x{}".format(hex(self.C)[2:].zfill(8).upper()),
                  self.CT, self.ST, self.Bx, str_B
                  ]

        result = "\t".join([str(x) for x in result])
        return result


def compress(fname, oname, table):

    ptable = lookuptable[table]
    enc = Encoder(ptable())

    # open file to compress
    with open(fname) as f:
        bits = bs.ConstBitStream(f)

    # compress file to memory
    for val in bits.bin:
        enc.encode(int(val))
        print(enc)

    # write compressed stream to disk
    with open(oname,'wb') as f:
        enc.flush()
        enc.out.append(hex(0xff))
        enc.out.append(hex(0xd9))
        enc.out.append(bs.BitString(uint=0, length=8))
        enc.out.tofile(f)


if __name__ == "__main__":

    fname = './tests/test.raw'
    oname = './tests/test.raw.qmenc'

    compress(fname, oname, 'jpeg')