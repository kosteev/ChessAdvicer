import json

import termcolor

from pieces import PIECES, WHITE, BLACK


def color_sign(color):
    '''
    Returns 1 for white and -1 for black.
    Used in many functions, e.g.: get_pieces_eval
    '''
    return 1 if color == WHITE else -1


def normalize_cell(cell, move_up_color):
    '''
    Normalizes cell relative to a8 square.
    '''
    if move_up_color == BLACK:
        cell = (7 - cell[0], 7 - cell[1])

    return cell


def h_name(cell, move_up_color):
    cell = normalize_cell(cell, move_up_color)
    return 8 - cell[1]


def v_name(cell, move_up_color):
    cell = normalize_cell(cell, move_up_color)
    return chr(ord('a') + cell[0])


def name_to_cell(name, move_up_color):
    cell = (ord(name[0]) - ord('a'), 8 - int(name[1]))
    cell = normalize_cell(cell, move_up_color)

    return cell


def cell_name(cell, move_up_color):
    return '{}{}'.format(v_name(cell, move_up_color), h_name(cell, move_up_color))


def format_move(move, move_up_color):
    if move['piece'] == 'pawn':
        if move['new_position_old_piece']:
            piece_title = v_name(move['position'], move_up_color)
        else:
            piece_title = ''
    else:
        piece_title = PIECES[move['piece']]['title']

    return '{piece_title}{is_take}{new_position}{new_piece_title}{check_mate}'.format(
        piece_title=piece_title,
        is_take='x' if move['new_position_old_piece'] else '',
        new_position=cell_name(move['new_position'], move_up_color),
        new_piece_title=('=' + PIECES[move['new_piece']]['title']) if move['piece'] != move['new_piece'] else '',
        check_mate=''
    )


def moves_stringify(moves, move_up_color):
    # TODO: 1.Bf5 f4 2.Kf6 ...
    return '; '.join(
        [format_move(move, move_up_color)
         for move in reversed(moves)])


def get_pieces_hash(board):
    # TODO: consider all board params
    if board is None:
        return -1337

    return hash(json.dumps(sorted(board.pieces.items())))


def print_board(board):
    BOARD_COLORS = {
        WHITE: 'cyan',
        BLACK: 'grey'
    }

    for y in xrange(8):
        line = ''
        for x in xrange(8):
            p = board.pieces.get((x, y))
            if p is None:
                line += '.'
            else:
                line += termcolor.colored(PIECES[p[0]]['title'], BOARD_COLORS[p[1]])
        print line
