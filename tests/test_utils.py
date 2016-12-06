import unittest
from nose.tools import assert_equal

from pieces import WHITE, BLACK
from utils import name_to_cell, cell_name, format_move, moves_stringify



class Test(unittest.TestCase):
    def test_name_cell(self):
        inputs = [
            ('a8', WHITE, (0, 0)),
            ('c4', WHITE, (2, 4)),
            ('c4', BLACK, (5, 3)),
            ('h1', BLACK, (0, 0)),
            ('g5', WHITE, (6, 3))
        ]
        for name, move_up_color, cell in inputs:
            assert_equal(name_to_cell(name, move_up_color), cell)
            assert_equal(cell_name(cell, move_up_color), name)

    def test_format_move(self):
        inputs = [
            ({
                'position': (4, 6),
                'new_position': (4, 4),
                'piece': 'pawn',
                'new_piece': 'pawn',
                'new_position_old_piece': None
            }, WHITE, 'e4'),
            ({
                'position': (4, 6),
                'new_position': (3, 5),
                'piece': 'pawn',
                'new_piece': 'pawn',
                'new_position_old_piece': ('rook', BLACK)
            }, WHITE, 'exd3'),
            ({
                'position': (4, 1),
                'new_position': (4, 0),
                'piece': 'pawn',
                'new_piece': 'knight',
                'new_position_old_piece': None
            }, WHITE, 'e8=N'),
            ({
                'position': (1, 2),
                'new_position': (6, 7),
                'piece': 'bishop',
                'new_piece': 'bishop',
                'new_position_old_piece': ('queen', WHITE)
            }, BLACK, 'Bxb8'),
        ]
        for move, move_up_color, text in inputs:
            assert_equal(format_move(move, move_up_color), text)

    def test_moves_stringify(self):
        input_1 = ([{
            'position': (4, 6),
            'new_position': (4, 4),
            'piece': 'pawn',
            'new_piece': 'pawn',
            'new_position_old_piece': None
        }, {
            'position': (3, 3),
            'new_position': (4, 4),
            'piece': 'pawn',
            'new_piece': 'pawn',
            'new_position_old_piece': ('pawn', WHITE)
        }, {
            'position': (0, 1),
            'new_position': (0, 6),
            'piece': 'rook',
            'new_piece': 'rook',
            'new_position_old_piece': None
        }, {
            'position': (2, 5),
            'new_position': (0, 6),
            'piece': 'knight',
            'new_piece': 'knight',
            'new_position_old_piece': ('rook', WHITE)
        }], WHITE, WHITE, '1.e4 dxe4 2.Ra2 Nxa2')

        input_2 = ([{
            'position': (6, 1),
            'new_position': (7, 2),
            'piece': 'pawn',
            'new_piece': 'pawn',
            'new_position_old_piece': ('knight', WHITE)
        }, {
            'position': (3, 6),
            'new_position': (7, 2),
            'piece': 'queen',
            'new_piece': 'queen',
            'new_position_old_piece': ('pawn', BLACK)
        }], BLACK, WHITE, 'gxh6 2.Qxh6')

        inputs = [input_1, input_2]
        for moves, move_color, move_up_color, text in inputs:
            assert_equal(moves_stringify(list(reversed(moves)), move_color, move_up_color), text)
