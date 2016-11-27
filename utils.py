import json

import termcolor

from pieces import PIECES, WHITE, BLACK


def color_sign(color):
    return 1 if color == WHITE else -1


def get_pieces_eval(board):
    '''
    pieces = {(1, 2): ('rook', 'white)}
    '''
    total = 0
    for (piece, color) in board['pieces'].values():
        if color == WHITE:
            total += PIECES[piece]['value']
        else:
            total -= PIECES[piece]['value']

    return total


def h_name(cell, move_up_color):
    if move_up_color == WHITE:
        return 8 - cell[1]
    else:
        return cell[1] + 1


def v_name(cell, move_up_color):
    if move_up_color == WHITE:
        return chr(ord('a') + cell[0])
    else:
        return chr(ord('h') - cell[0])


def cell_name(cell, move_up_color):
    return '{}{}'.format(v_name(cell, move_up_color), h_name(cell, move_up_color))


def format_move(move, move_up_color):
    if move['piece'] == 'pawn':
        if move['is_take']:
            piece_title = v_name(move['position'], move_up_color)
        else:
            piece_title = ''
    else:
        piece_title = PIECES[move['piece']]['title']

    return '{piece_title}{is_take}{new_position}{new_piece_title}{check_mate}'.format(
        piece_title=piece_title,
        is_take='x' if move['is_take'] else '',
        new_position=cell_name(move['new_position'], move_up_color),
        new_piece_title=('=' + PIECES[move['new_piece']]['title']) if move['piece'] != move['new_piece'] else '',
        check_mate=''
    )


def get_pieces_hash(board):
    if board is None:
        return -1337

    return hash(json.dumps(sorted(board['pieces'].items())))


def print_board(board):
    BOARD_COLORS = {
        WHITE: 'cyan',
        BLACK: 'grey'
    }

    for y in xrange(8):
        line = ''
        for x in xrange(8):
            p = board['pieces'].get((x, y))
            if p is None:
                line += '.'
            else:
                line += termcolor.colored(PIECES[p[0]]['title'], BOARD_COLORS[p[1]])
        print line


def on_board((c, r)):
    return 0 <= c < 8 and 0 <= r < 8
