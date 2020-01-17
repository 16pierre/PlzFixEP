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
from database import *

_TEST_VITALIC = bytes.fromhex("00000081789c7378dad1c000048ea9553b40342303043001f1029bec3707fefc87007126a80c43c261bfda544761389f81e17f3d9c49b23e00fe93225b")

class TestDatabase(unittest.TestCase):

    def test_idenpotent(self):
        self.assertEqual(
            compress(bytes.fromhex(uncompress(_TEST_VITALIC))),
            _TEST_VITALIC)
