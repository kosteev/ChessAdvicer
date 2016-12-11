import unittest
from nose.tools import assert_equal

from pieces import COUNT_OF_PROBABLE_MOVES, PROBABLE_MOVES


class Test(unittest.TestCase):
    def test_probable_moves(self):
        d = {}
        d[('rook', (1, 3))] = [
            [{'new_position': (1 + x, 3)} for x in xrange(1, 7)],
            [{'new_position': (1 - x, 3)} for x in xrange(1, 2)],
            [{'new_position': (1, 3 + x)} for x in xrange(1, 5)],
            [{'new_position': (1, 3 - x)} for x in xrange(1, 4)]
        ]
        d[('bishop', (1, 3))] = [
            [{'new_position': (1 + x, 3 + x)} for x in xrange(1, 5)],
            [{'new_position': (1 - x, 3 + x)} for x in xrange(1, 2)],
            [{'new_position': (1 + x, 3 - x)} for x in xrange(1, 4)],
            [{'new_position': (1 - x, 3 - x)} for x in xrange(1, 2)],
        ]
        d[('queen', (1, 3))] = d[('rook', (1, 3))] + d[('bishop', (1, 3))]
        d[('knight', (1, 3))] = [
            [{'new_position': (2, 5)}], [{'new_position': (2, 1)}],
            [{'new_position': (0, 5)}], [{'new_position': (0, 1)}],
            [{'new_position': (3, 4)}], [{'new_position': (3, 2)}]
        ]
        d[('king', (1, 3))] = [
            [{'new_position': (1, 4)}], [{'new_position': (1, 2)}],
            [{'new_position': (2, 4)}], [{'new_position': (2, 3)}], [{'new_position': (2, 2)}],
            [{'new_position': (0, 4)}], [{'new_position': (0, 3)}], [{'new_position': (0, 2)}]
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
