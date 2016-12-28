import unittest
from nose.tools import assert_equal

from evaluation import take_evaluation
from mocks import get_mock
from utils import print_board


class Test(unittest.TestCase):
    def test_evaluation(self):
        board = get_mock(0)
        print_board(board)

        assert_equal(take_evaluation(board)['result'], {
            'evaluation': -2.006,
            'moves': [{'captured_piece': 'pawn',
                'captured_position': (0, 1),
                'new_piece': 'pawn',
                'new_position': (0, 1),
                'piece': 'pawn',
                'position': (1, 2)}]
        })

    def test_evaluation_1(self):
        board = get_mock(1)
        print_board(board)

        assert_equal(take_evaluation(board)['result'], {
            'evaluation': 0,
            'moves': []
        })

    def test_evaluation_2(self):
        board = get_mock(2)
        print_board(board)

        assert_equal(take_evaluation(board)['result'], {
            'evaluation': 5.014,
            'moves': []
        })

    def test_evaluation_3(self):
        board = get_mock(3)
        print_board(board)

        assert_equal(take_evaluation(board)['result'], {
            'evaluation': 16.038,
            'moves': [{
                'position': (6, 5),
                'new_position': (5, 6),
                'piece': 'pawn',
                'new_piece': 'pawn',
                'captured_piece': 'knight',
                'captured_position': (5, 6)
            }]
        })
