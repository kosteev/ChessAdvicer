import unittest
from nose.tools import assert_equal

from evaluation import take_evaluation
from mocks import get_mock
from pieces import WHITE, BLACK
from utils import print_board


class Test(unittest.TestCase):
    def test_evaluation(self):
        board = get_mock(0)
        print_board(board)

        assert_equal(take_evaluation(board)['result'], {
            'evaluation': -1.008,
            'moves': []
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
            'evaluation': 15.049,
            'moves': [{
                'position': (5, 6),
                'new_position': (7, 7),
                'piece': 'knight',
                'new_piece': 'knight',
                'captured_piece': 'knight',
                'captured_position': (7, 7)
            }, {
                'position': (3, 4),
                'new_position': (2, 4),
                'piece': 'queen',
                'new_piece': 'queen',
                'captured_piece': 'rook',
                'captured_position': (2, 4)
            }]
        })
