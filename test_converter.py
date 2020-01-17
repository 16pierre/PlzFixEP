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

