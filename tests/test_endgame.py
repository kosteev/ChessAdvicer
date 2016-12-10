import unittest
from nose.tools import assert_equal

from endgame import get_syzygy_best_move
from mocks import get_mock



class Test(unittest.TestCase):
    def test_one_pawn(self):
        board = get_mock(4)

        result = get_syzygy_best_move(board)
        assert_equal({
            'position': (3, 4),
            'new_position': (2, 5),
            'piece': 'king',
            'new_piece': 'king',
            'captured_piece': None
        }, result['moves'][0])

    def test_promotion_rook(self):
        board = get_mock(5)

        result = get_syzygy_best_move(board)
        assert_equal({
            'position': (5, 6),
            'new_position': (5, 7),
            'piece': 'pawn',
            'new_piece': 'rook',
            'captured_piece': None
        }, result['moves'][0])
