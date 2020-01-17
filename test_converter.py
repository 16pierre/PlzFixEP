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

import unittest
from converter import *

class TestConverter(unittest.TestCase):

    def test_hex_to_bin(self):
        self.assertEqual(hex_to_bin("1A"), b'\x1a')
        self.assertEqual(hex_to_bin("FF00"), b'\xff\x00')

    def test_bin_to_double(self):
        self.assertEqual(bin_to_double_big_endian(hex_to_bin("40637947AE147AE1")), 155.79)
        self.assertEqual(bin_to_double_big_endian(hex_to_bin("0000000000000000")), 0.0)

        self.assertEqual(bin_to_double_little_endian(hex_to_bin("E17A14AE47796340")), 155.79)
        self.assertEqual(bin_to_double_little_endian(hex_to_bin("0000000000000000")), 0.0)

    def test_to_sint(self):
        self.assertEqual(bin_to_sint_big_endian(hex_to_bin("FFFFFFFF")), -1)
        self.assertEqual(bin_to_sint_big_endian(hex_to_bin("FFFFFF9C")), -100)
        self.assertEqual(bin_to_sint_big_endian(hex_to_bin("000003E8")), 1000)

        self.assertEqual(bin_to_sint_little_endian(hex_to_bin("FFFFFFFF")), -1)
        self.assertEqual(bin_to_sint_little_endian(hex_to_bin("9CFFFFFF")), -100)
        self.assertEqual(bin_to_sint_little_endian(hex_to_bin("E8030000")), 1000)

    def test_bytes_from_hexstring(self):
        self.assertEqual(read_bytes_from_hexstring("FF", 1), (b'\xff', ""))
        self.assertEqual(read_bytes_from_hexstring("FFAA", 1), (b'\xff', "AA"))
        self.assertEqual(read_bytes_from_hexstring("FFAA", 2), (b'\xff\xaa', ""))
        self.assertEqual(read_bytes_from_hexstring("FFAABB", 2), (b'\xff\xaa', "BB"))

