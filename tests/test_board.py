import unittest
from nose.tools import assert_equal, assert_true

from board import Board
from mocks import MOCKS_COUNT, get_mock
from pieces import WHITE, BLACK
from utils import print_board


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
        b1 = Board(pieces, move_color=WHITE, en_passant=None)
        b2 = Board(pieces, move_color=BLACK, en_passant=None)
        b3 = Board(pieces, move_color=BLACK, en_passant=(2, 2))

        assert_equal(len({b1.hash, b2.hash, b3.hash}), 3)

    def test_complex(self):
        board = get_mock(3)
        print_board(board)

        d = [{
            'move': {
                'position': (3, 4),
                'new_position': (2, 4),
                'piece': 'queen',
                'new_piece': 'queen',
                'captured_piece': 'rook',
                'captured_position': (2, 4)
            },
            'evaluation': 18,
            'probable_moves_count': 44
        }, {
            'move': {
                'position': (6, 5),
                'new_position': (5, 6),
                'piece': 'pawn',
                'new_piece': 'pawn',
                'captured_piece': 'knight',
                'captured_position': (5, 6)
            },
            'evaluation': 16,
            'probable_moves_count': 38
        }, {
            'move': {
                'position': (7, 7),
                'new_position': (5, 6),
                'piece': 'knight',
                'new_piece': 'knight',
                'captured_piece': 'knight',
                'captured_position': (5, 6)
            },
            'evaluation': 16,
            'probable_moves_count': 42
        }, {
            'move': {
                'position': (6, 6),
                'new_position': (5, 6),
                'piece': 'rook',
                'new_piece': 'rook',
                'captured_piece': 'knight',
                'captured_position': (5, 6)
            },
            'evaluation': 16,
            'probable_moves_count': 38
        }]

        cnt = 0
        assert_equal(board.evaluation, 13)
        for move in board.generate_next_board(capture_sort_key=Board.sort_take_by_value):
            if cnt < len(d):
                assert_equal(move, d[cnt]['move'])
                assert_equal(board.evaluation, d[cnt]['evaluation'])
                assert_equal(board.probable_moves_count, d[cnt]['probable_moves_count'])
            else:
                assert_equal(board.evaluation, 13)
            cnt += 1

    def test_en_passant(self):
        board = get_mock(7)
        print_board(board)

        assert_equal(board.en_passant, (6, 2))
        assert_equal(board.evaluation, 4)
        assert_equal(board.probable_moves_count, 3)
        assert_true(board.pieces[(6, 3)] == ('pawn', WHITE))
        cnt = 0
        for move in board.generate_next_board(capture_sort_key=Board.sort_take_by_value):
            if cnt == 0:
                assert_equal(move['piece'], 'pawn')
                assert_equal(move['new_position'], (6, 2))
                assert_equal(move['captured_piece'], 'pawn')
                assert_equal(board.evaluation, 3)
                assert_equal(board.probable_moves_count, 1)
                assert_true((6, 3) not in board.pieces)
            cnt += 1
        assert_true(board.pieces[(6, 3)] == ('pawn', WHITE))
