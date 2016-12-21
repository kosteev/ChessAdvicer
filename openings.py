from board import Board
from mocks import get_mock
from pieces import WHITE
from utils import name_to_cell, get_color_pieces


OPENINGS = [{
    'name': 'fiancetto',
    'color': WHITE,
    'from_to': [
        ('g1', 'f3'),
        ('g2', 'g3'),
        ('f1', 'g2'),
        ('e1', 'g1')
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


def get_opening_move(board):
    '''
    Returns opening valid move (check is supposed to be verified additionally).
    '''
    moves_dict = {}
    for move in board.get_board_moves():
        moves_dict[(move['position'], move['new_position'])] = move

    color_pieces = get_color_pieces(board.pieces, board.move_color)
    pieces_hash = Board.pieces_hash(color_pieces)

    for opening in OPENINGS:
        for ind, move_hash in enumerate(opening['hashes']):
            if move_hash == pieces_hash:
                name_from, name_to = opening['from_to'][ind]
                position = name_to_cell(name_from)
                new_position = name_to_cell(name_to)

                move = moves_dict.get((position, new_position))
                return move

    return None
