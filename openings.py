import random

from board import Board
from mocks import get_mock
from pieces import WHITE, BLACK
from utils import name_to_cell, get_color_pieces


OPENINGS = [{
    'name': 'fiancetto_white',
    'color': WHITE,
    'from_to': [
        ('g1', 'f3'),
        ('g2', 'g3'),
        ('f1', 'g2'),
        ('e1', 'g1'),
        ('e2', 'e4')
    ]
}, {
    'name': 'fiancetto_black',
    'color': BLACK,
    'from_to': [
        ('g8', 'f6'),
        ('g7', 'g6'),
        ('f8', 'g7'),
        ('e8', 'g8'),
        ('e7', 'e5')
    ]
}, {
    'name': 'e2e3_castle',
    'color': WHITE,
    'from_to': [
        ('g1', 'f3'),
        ('e2', 'e3'),
        ('f1', 'e2'),
        ('e1', 'g1'),
        ('d2', 'd4')
    ]
}, {
    'name': 'e4d4',
    'color': WHITE,
    'from_to': [
        ('e2', 'e4'),
        ('d2', 'd4')
    ]
}, {
    'name': 'e7e5',
    'color': WHITE,
    'from_to': [
        ('e7', 'e5'),
        ('d7', 'd5')
    ]
}]

for opening in OPENINGS:
    board = get_mock(1)
    color_pieces = get_color_pieces(board.pieces, opening['color'])

    hashes = []
    for name_from, name_to in opening['from_to']:
        hashes.append(Board.pieces_hash(color_pieces))

        position = name_to_cell(name_from)
        new_position = name_to_cell(name_to)

        color_pieces[new_position] = color_pieces[position]
        del color_pieces[position]

    opening['hashes'] = hashes


def get_opening_info(board):
    '''
    Returns opening valid move (check is supposed to be verified additionally).
    '''
    available_moves_dict = {}
    for move in board.get_board_moves():
        available_moves_dict[(move['position'], move['new_position'])] = move

    color_pieces = get_color_pieces(board.pieces, board.move_color)
    pieces_hash = Board.pieces_hash(color_pieces)

    opening_infos = []
    for opening in OPENINGS:
        for ind, move_hash in enumerate(opening['hashes']):
            if move_hash == pieces_hash:
                name_from, name_to = opening['from_to'][ind]
                position = name_to_cell(name_from)
                new_position = name_to_cell(name_to)

                move = available_moves_dict.get((position, new_position))
                if move:
                    opening_infos.append({
                        'name': opening['name'],
                        'move': move
                    })
                break

    if opening_infos:
        return random.choice(opening_infos)

    return None
