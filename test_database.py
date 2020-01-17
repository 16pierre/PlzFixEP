import unittest
from database import *

_TEST_VITALIC = bytes.fromhex("00000081789c7378dad1c000048ea9553b40342303043001f1029bec3707fefc87007126a80c43c261bfda544761389f81e17f3d9c49b23e00fe93225b")

class TestDatabase(unittest.TestCase):

    def test_idenpotent(self):
        self.assertEqual(
            compress(bytes.fromhex(uncompress(_TEST_VITALIC))),
            _TEST_VITALIC)
