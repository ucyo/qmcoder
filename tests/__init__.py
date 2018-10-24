
import os
import bitstring as bs

folder = os.path.dirname(__file__)

with open(os.path.join(folder, 'test.raw'), 'rb') as f:
    test = f.read()
    test = [int(x) for x in bs.BitArray(test).bin]


with open(os.path.join(folder, 'test.raw.compressed'), 'rb') as f:
    expected = f.read()
    # expected = [int(x) for x in bs.BitArray(test).bin]