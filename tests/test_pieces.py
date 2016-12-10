import unittest
from nose.tools import assert_equal

from pieces import COUNT_OF_PROBABLE_MOVES, PROBABLE_MOVES


class Test(unittest.TestCase):
    def test_probable_moves(self):
        d = {}
        d[('rook', (1, 3))] = [
            [(1 + x, 3, None) for x in xrange(1, 7)],
            [(1 - x, 3, None) for x in xrange(1, 2)],
            [(1, 3 + x, None) for x in xrange(1, 5)],
            [(1, 3 - x, None) for x in xrange(1, 4)]
        ]
        d[('bishop', (1, 3))] = [
            [(1 + x, 3 + x, None) for x in xrange(1, 5)],
            [(1 - x, 3 + x, None) for x in xrange(1, 2)],
            [(1 + x, 3 - x, None) for x in xrange(1, 4)],
            [(1 - x, 3 - x, None) for x in xrange(1, 2)],
        ]
        d[('queen', (1, 3))] = d[('rook', (1, 3))] + d[('bishop', (1, 3))]
        d[('knight', (1, 3))] = [
            [(2, 5, None)], [(2, 1, None)],
            [(0, 5, None)], [(0, 1, None)],
            [(3, 4, None)], [(3, 2, None)]
        ]
        d[('king', (1, 3))] = [
            [(1, 4, None)], [(1, 2, None)],
            [(2, 4, None)], [(2, 3, None)], [(2, 2, None)],
            [(0, 4, None)], [(0, 3, None)], [(0, 2, None)]
        ]
        for (piece, position), variants in d.items():
            assert_equal(sorted(variants), sorted(PROBABLE_MOVES[piece][position]))

        assert_equal(COUNT_OF_PROBABLE_MOVES['rook'][(2, 2)], 14)
        assert_equal(COUNT_OF_PROBABLE_MOVES['rook'][(4, 3)], 14)

        assert_equal(COUNT_OF_PROBABLE_MOVES['knight'][(0, 0)], 2)
        assert_equal(COUNT_OF_PROBABLE_MOVES['knight'][(3, 3)], 8)
        assert_equal(COUNT_OF_PROBABLE_MOVES['knight'][(1, 7)], 3)
        assert_equal(COUNT_OF_PROBABLE_MOVES['knight'][(2, 0)], 4)

        assert_equal(COUNT_OF_PROBABLE_MOVES['bishop'][(0, 0)], 7)
        assert_equal(COUNT_OF_PROBABLE_MOVES['bishop'][(3, 3)], 13)
        assert_equal(COUNT_OF_PROBABLE_MOVES['bishop'][(1, 7)], 7)
        assert_equal(COUNT_OF_PROBABLE_MOVES['bishop'][(2, 0)], 7)

        assert_equal(COUNT_OF_PROBABLE_MOVES['queen'][(0, 0)], 21)
        assert_equal(COUNT_OF_PROBABLE_MOVES['queen'][(3, 3)], 27)
        assert_equal(COUNT_OF_PROBABLE_MOVES['queen'][(1, 7)], 21)
        assert_equal(COUNT_OF_PROBABLE_MOVES['queen'][(2, 0)], 21)

        assert_equal(COUNT_OF_PROBABLE_MOVES['king'][(0, 0)], 3)
        assert_equal(COUNT_OF_PROBABLE_MOVES['king'][(3, 3)], 8)
        assert_equal(COUNT_OF_PROBABLE_MOVES['king'][(1, 7)], 5)
        assert_equal(COUNT_OF_PROBABLE_MOVES['king'][(2, 0)], 5)

        assert_equal(COUNT_OF_PROBABLE_MOVES['pawn'][(3, 3)], 2)
        assert_equal(COUNT_OF_PROBABLE_MOVES['pawn'][(1, 2)], 2)
        assert_equal(COUNT_OF_PROBABLE_MOVES['pawn'][(0, 2)], 1)
        assert_equal(COUNT_OF_PROBABLE_MOVES['pawn'][(7, 4)], 1)
