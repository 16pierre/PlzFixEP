import unittest
from beat_data import *

_TEST_VITALIC = "40e588800000000041657ab800000000010000000000000002000000a03c6becc0fcffffffffffffff1702000000000000000060c34e7d6541130200000000000000000000ff7f00000000000000000002000000a03c6becc0fcffffffffffffff1702000000000000000060c34e7d6541130200000000000000000000ff7f0000"

class TestBeatData(unittest.TestCase):

    def test_idenpotent(self):
        self.assertEqual(
            BeatData(_TEST_VITALIC).to_bytes(),
            bytes.fromhex(_TEST_VITALIC))

