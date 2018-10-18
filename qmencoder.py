import numpy as np
from functools import namedtuple as nt

LPS = nt('LPS', 'sym')
MPS = nt('MPS', 'sym')


class Range(object):

    def __init__(self, C=0, A=1, Qe=.5):
        self.C = C
        self.A = A
        self.Qe = Qe
        self.count = 0

    def encode(self, val):
        if isinstance(val, MPS):
            self.A -= self.Qe
            if self.A < .75:
                if self.A < self.Qe:
                    self.C += self.A
                    self.A = self.Qe
                self.renormalize()
        elif isinstance(val, LPS):
            self.A -= self.Qe
            if self.A >= self.Qe:
                self.C += self.A
                self.A = self.Qe
            self.renormalize()
        self.count += 1
        return self

    def renormalize(self):
        while self.A < .75:
            self.A *= 2
            self.C *= 2

    # def decode(self):
    #     LPS = nt('LPS', 'sym')
    #     MPS = nt('MPS', 'sym')
    #     lps = LPS(None)
    #     mps = MPS(None)

    #     self.A = 1
    #     while self.count>0:
    #         self.count -= 1
    #         dl = self.A * (1-self.Qe)

    #         print(self.C, self.A, dl)
    #         while self.A <.75:
    #             self.C /= 2
    #             self.A *= 2
    #         if self.C >= dl:
    #             yield lps
    #             self.C = self.C - self.A * (1 - self.Qe)
    #             self.A = self.A * self.Qe
    #         else:
    #             yield mps
    #             self.A = self.A * (1 - self.Qe)


if __name__ == '__main__':
    lps = LPS(1)
    mps = MPS(0)
    k = Range(Qe=.1)
    k.encode(lps).encode(mps).encode(lps).encode(mps)
    print(k.C, k.A)