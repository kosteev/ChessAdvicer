import unittest
from nose.tools import assert_equal

from board import Board
from mocks import MOCKS_COUNT, get_mock
from pieces import WHITE, BLACK


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

    def test_complex(self):
        board = get_mock(3)

        d = [{
            'move': {
                'position': (3, 4),
                'new_position': (2, 4),
                'piece': 'queen',
                'new_piece': 'queen',
                'captured_piece': 'rook'
            },
            'evaluation': 18,
            'probable_moves_count': 47
        }, {
            'move': {
                'position': (6, 5),
                'new_position': (5, 6),
                'piece': 'pawn',
                'new_piece': 'pawn',
                'captured_piece': 'knight'
            },
            'evaluation': 16,
            'probable_moves_count': 41
        }, {
            'move': {
                'position': (7, 7),
                'new_position': (5, 6),
                'piece': 'knight',
                'new_piece': 'knight',
                'captured_piece': 'knight'
            },
            'evaluation': 16,
            'probable_moves_count': 45
        }, {
            'move': {
                'position': (6, 6),
                'new_position': (5, 6),
                'piece': 'rook',
                'new_piece': 'rook',
                'captured_piece': 'knight'
            },
            'evaluation': 16,
            'probable_moves_count': 41
        }]

        cnt = 0
        assert_equal(board.evaluation, 13)
        for move in board.generate_next_board(sort_key=Board.sort_by_take_value):
            if cnt < len(d):
                assert_equal(move, d[cnt]['move'])
                assert_equal(board.evaluation, d[cnt]['evaluation'])
                assert_equal(board.probable_moves_count, d[cnt]['probable_moves_count'])
            else:
                assert_equal(board.evaluation, 13)
            cnt += 1
