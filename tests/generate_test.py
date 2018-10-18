#!/usr/bin/env python
# coding: utf-8
"""
Generating test data from the official ISO definition.
"""

import bitstring as bs

testbits = bs.BitArray()

raw = [
'0x00020051',
'0x000000C0',
'0x0352872A',
'0xAAAAAAAA',
'0x82C02000',
'0xFCD79EF6',
'0x74EAABF7',
'0x697EE74C',
]

compressed = [
'0x655B5144',
'0xF7969D51',
'0x7855BFFF',
'0x00FC5184',
'0xC7CEF939',
'0x00287D46',
'0x708ECBC0',
'0xF6FFD900',
]

raw_ba = bs.BitArray()
_ = [raw_ba.append(x) for x in raw]

with open('test.raw', 'wb') as f:#, buffering, encoding, errors, newline, closefd, opener)
    raw_ba.tofile(f)

comp_ba = bs.BitArray()
_ = [comp_ba.append(x) for x in compressed]

with open('test.raw.compressed', 'wb') as f:#, buffering, encoding, errors, newline, closefd, opener)
    comp_ba.tofile(f)