import unittest
from nose.tools import assert_equal

from pieces import WHITE, BLACK
from mocks import MOCKS_COUNT, get_mock
from board import Board



class Test(unittest.TestCase):
    def test_hash(self):
        hashes = set()
        for mock_id in xrange(MOCKS_COUNT):
            hashes.add(get_mock(mock_id).hash)

        assert_equal(len(hashes), MOCKS_COUNT)

        pieces = {
            (0, 0): ('king', WHITE),
            (7, 6): ('king', BLACK)
        }
        b1 = Board(pieces, move_color=WHITE)
        b2 = Board(pieces, move_color=BLACK)

        assert_equal(len({b1.hash, b2.hash}), 2)
