"""
PlzFixEP is an open-source helper to import data into Engine Prime
Copyright (C) 2020  Quentin PIERRE

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import struct
import binascii

"""
A bunch of utils to convert binaries etc.
Makes my eyes bleed
"""

def hex_to_bin(hex_str):
    return (int(hex_str, 16)).to_bytes(len(hex_str)//2, byteorder='big')

assert hex_to_bin("1A") == b'\x1a'
assert hex_to_bin("FF00") == b'\xff\x00'

def bin_to_double_little_endian(bin_str):
    return struct.unpack('<d', bin_str)[0]
def bin_to_double_big_endian(bin_str):
    return struct.unpack('>d', bin_str)[0]

def bin_to_sint_little_endian(bin_str):
    return struct.unpack('<i', bin_str)[0]
def bin_to_sint_big_endian(bin_str):
    return struct.unpack('>i', bin_str)[0]

def float_to_double_little_endian(float_val):
    return struct.pack('<d', float_val)
def float_to_double_big_endian(float_val):
    return struct.pack('>d', float_val)

def sint_to_little_endian(sint_val):
    return struct.pack('<i', sint_val)
def sint_to_big_endian(sint_val):
    return struct.pack('>i', sint_val)

assert bin_to_double_big_endian(hex_to_bin("0000000000000000")) == 0.0
assert bin_to_double_big_endian(hex_to_bin("40637947AE147AE1")) == 155.79

assert bin_to_double_little_endian(hex_to_bin("0000000000000000")) == 0.0
assert bin_to_double_little_endian(hex_to_bin("E17A14AE47796340")) == 155.79

assert bin_to_sint_big_endian(hex_to_bin("FFFFFFFF")) == -1
assert bin_to_sint_big_endian(hex_to_bin("FFFFFF9C")) == -100
assert bin_to_sint_big_endian(hex_to_bin("000003E8")) == 1000

assert bin_to_sint_little_endian(hex_to_bin("FFFFFFFF")) == -1
assert bin_to_sint_little_endian(hex_to_bin("9CFFFFFF")) == -100
assert bin_to_sint_little_endian(hex_to_bin("E8030000")) == 1000

def read_bytes_from_hexstring(string, nb_bytes):
    return hex_to_bin(string[:nb_bytes*2]), string[nb_bytes*2:]

assert read_bytes_from_hexstring("FF", 1) == (b'\xff', "")
assert read_bytes_from_hexstring("FFAA", 1) == (b'\xff', "AA")
assert read_bytes_from_hexstring("FFAA", 2) == (b'\xff\xaa', "")
assert read_bytes_from_hexstring("FFAABB", 2) == (b'\xff\xaa', "BB")

