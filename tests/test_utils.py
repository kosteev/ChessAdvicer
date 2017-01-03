import unittest
from nose.tools import assert_equal

from mocks import get_mock, MOCKS_COUNT, FENS
from pieces import WHITE, BLACK
from utils import name_to_cell, cell_name, format_move, moves_stringify, get_fen_from_board, get_board_from_fen


class Test(unittest.TestCase):
    def test_name_cell(self):
        inputs = [
            ('a1', (0, 0)),
            ('c4', (2, 3)),
            ('h1', (7, 0)),
            ('g5', (6, 4))
        ]
        for name, cell in inputs:
            assert_equal(name_to_cell(name), cell)
            assert_equal(cell_name(cell), name)

    def test_format_move(self):
        board = get_mock(19)
        inputs = [
            ({
                'position': (5, 3),
                'new_position': (6, 3),
                'piece': 'queen',
                'new_piece': 'queen',
                'captured_piece': None,
                'captured_position': (6, 3)
            }, 'Qfg4'),
            ({
                'position': (7, 5),
                'new_position': (6, 3),
                'piece': 'knight',
                'new_piece': 'knight',
                'captured_piece': 'queen',
                'captured_position': (6, 3)
            }, 'N6xg4'),
            ({
                'position': (4, 1),
                'new_position': (4, 3),
                'piece': 'pawn',
                'new_piece': 'pawn',
                'captured_piece': None,
                'captured_position': (4, 3)
            }, 'e4'),
            ({
                'position': (3, 3),
                'new_position': (4, 2),
                'piece': 'pawn',
                'new_piece': 'pawn',
                'captured_piece': 'pawn',
                'captured_position': (4, 3)
            }, 'dxe3'),
            ({
                'position': (1, 6),
                'new_position': (1, 7),
                'piece': 'pawn',
                'new_piece': 'queen',
                'captured_piece': None,
                'captured_position': (1, 7)
            }, 'b8=Q+'),
            ({
                'position': (2, 6),
                'new_position': (1, 7),
                'piece': 'bishop',
                'new_piece': 'bishop',
                'captured_piece': 'queen',
                'captured_position': (1, 7)
            }, 'Bxb8'),
            ({
                'position': (4, 0),
                'new_position': (2, 0),
                'piece': 'king',
                'new_piece': 'king',
                'captured_piece': None,
                'captured_position': (2, 0)
            }, 'O-O-O'),
            ({
                'position': (4, 7),
                'new_position': (6, 7),
                'piece': 'king',
                'new_piece': 'king',
                'captured_piece': None,
                'captured_position': (6, 7)
            }, 'O-O'),
        ]
        for move, text in inputs:
            assert_equal(format_move(board, move), text)
            board.make_move(move)

    def test_moves_stringify(self):
        input_1 = ([{
            'position': (4, 1),
            'new_position': (4, 3),
            'piece': 'pawn',
            'new_piece': 'pawn',
            'captured_piece': None,
            'captured_position': (4, 3)
        }, {
            'position': (3, 4),
            'new_position': (4, 3),
            'piece': 'pawn',
            'new_piece': 'pawn',
            'captured_piece': 'pawn',
            'captured_position': (4, 3)
        }, {
            'position': (2, 1),
            'new_position': (0, 1),
            'piece': 'rook',
            'new_piece': 'rook',
            'captured_piece': None,
            'captured_position': (0, 1)
        }, {
            'position': (1, 3),
            'new_position': (0, 1),
            'piece': 'knight',
            'new_piece': 'knight',
            'captured_piece': 'rook',
            'captured_position': (0, 1)
        }], get_mock(20), '1.e4 dxe4 2.Ra2 Nxa2')

        input_2 = ([{
            'position': (3, 4),
            'new_position': (4, 5),
            'piece': 'queen',
            'new_piece': 'queen',
            'captured_piece': None,
            'captured_position': (4, 5)
        }, {
            'position': (6, 6),
            'new_position': (7, 5),
            'piece': 'pawn',
            'new_piece': 'pawn',
            'captured_piece': 'knight',
            'captured_position': (7, 5)
        }, {
            'position': (4, 5),
            'new_position': (6, 7),
            'piece': 'queen',
            'new_piece': 'queen',
            'captured_piece': None,
            'captured_position': (6, 7)
        }], get_mock(2), '1.Qe6 gxh6 2.Qg8+')

        input_3 = ([{
            'position': (3, 4),
            'new_position': (6, 7),
            'piece': 'queen',
            'new_piece': 'queen',
            'captured_piece': None,
            'captured_position': (6, 7)
        }, {
            'position': (5, 7),
            'new_position': (6, 7),
            'piece': 'rook',
            'new_piece': 'rook',
            'captured_piece': 'queen',
            'captured_position': (6, 7)
        }, {
            'position': (7, 5),
            'new_position': (5, 6),
            'piece': 'knight',
            'new_piece': 'knight',
            'captured_piece': None,
            'captured_position': (5, 6)
        }], get_mock(2), '1.Qg8+ Rxg8 2.Nf7#')

        inputs = [input_1, input_2, input_3]
        for moves, board, text in inputs:
            assert_equal(moves_stringify(board, list(reversed(moves))), text)

    def test_mock_fens(self):
        for ind in xrange(MOCKS_COUNT):
            board = get_mock(ind)
            assert_equal(get_fen_from_board(board), FENS[ind])

    def test_fen(self):
        for ind in xrange(MOCKS_COUNT):
            board = get_mock(ind)
            fen = get_fen_from_board(board)
            board_2 = get_board_from_fen(fen)
            fen_2 = get_fen_from_board(board_2)

            assert_equal(board.hash, board_2.hash)
            assert_equal(fen, fen_2)
