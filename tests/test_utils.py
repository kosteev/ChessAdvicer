import unittest
from nose.tools import assert_equal

from pieces import WHITE, BLACK
from utils import name_to_cell, cell_name, format_move, moves_stringify



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
        inputs = [
            ({
                'position': (4, 1),
                'new_position': (4, 3),
                'piece': 'pawn',
                'new_piece': 'pawn',
                'new_position_old_piece': None
            }, 'e4'),
            ({
                'position': (4, 1),
                'new_position': (3, 2),
                'piece': 'pawn',
                'new_piece': 'pawn',
                'new_position_old_piece': ('rook', BLACK)
            }, 'exd3'),
            ({
                'position': (4, 6),
                'new_position': (4, 7),
                'piece': 'pawn',
                'new_piece': 'knight',
                'new_position_old_piece': None
            }, 'e8=N'),
            ({
                'position': (6, 2),
                'new_position': (1, 7),
                'piece': 'bishop',
                'new_piece': 'bishop',
                'new_position_old_piece': ('queen', WHITE)
            }, 'Bxb8'),
        ]
        for move, text in inputs:
            assert_equal(format_move(move), text)

    def test_moves_stringify(self):
        input_1 = ([{
            'position': (4, 1),
            'new_position': (4, 3),
            'piece': 'pawn',
            'new_piece': 'pawn',
            'new_position_old_piece': None
        }, {
            'position': (3, 4),
            'new_position': (4, 3),
            'piece': 'pawn',
            'new_piece': 'pawn',
            'new_position_old_piece': ('pawn', WHITE)
        }, {
            'position': (0, 6),
            'new_position': (0, 1),
            'piece': 'rook',
            'new_piece': 'rook',
            'new_position_old_piece': None
        }, {
            'position': (2, 2),
            'new_position': (0, 1),
            'piece': 'knight',
            'new_piece': 'knight',
            'new_position_old_piece': ('rook', WHITE)
        }], WHITE, '1.e4 dxe4 2.Ra2 Nxa2')

        input_2 = ([{
            'position': (6, 6),
            'new_position': (7, 5),
            'piece': 'pawn',
            'new_piece': 'pawn',
            'new_position_old_piece': ('knight', WHITE)
        }, {
            'position': (4, 3),
            'new_position': (7, 5),
            'piece': 'queen',
            'new_piece': 'queen',
            'new_position_old_piece': ('pawn', BLACK)
        }], BLACK, 'gxh6 2.Qxh6')

        inputs = [input_1, input_2]
        for moves, move_color, text in inputs:
            assert_equal(moves_stringify(list(reversed(moves)), move_color), text)