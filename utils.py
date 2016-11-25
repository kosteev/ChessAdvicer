import json

from pieces import PIECES, WHITE, BLACK


MOVES = {}
MOVES['rook'] = [
    [(0, x, None) for x in xrange(1, 8)],
    [(0, -x, None) for x in xrange(1, 8)],
    [(x, 0, None) for x in xrange(1, 8)],
    [(-x, 0, None) for x in xrange(1, 8)]
]
MOVES['bishop'] = [
    [(x, x, None) for x in xrange(1, 8)],
    [(x, -x, None) for x in xrange(1, 8)],
    [(-x, x, None) for x in xrange(1, 8)],
    [(-x, -x, None) for x in xrange(1, 8)]
]
MOVES['queen'] = MOVES['rook'] + MOVES['bishop']
MOVES['king'] = [
    [(x, y, None)]
    for x in xrange(-1, 2)
    for y in xrange(-1, 2)
    if x != 0 or y != 0
]
MOVES['knight'] = [
    [(s1 * x, s2 * (3-x), None)]
    for x in xrange(1, 3)
    for s1 in [-1, 1]
    for s2 in [-1, 1]
]


MAX_EVALUATION = 1000


def get_pieces_eval(board):
    '''
    pieces = {(1, 2): ('rook', 'white)}
    '''
    total = 0
    for (piece, color) in board['pieces'].values():
        if color == board['move_up_color']:
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


def get_opp_color(color):
    return WHITE if color == BLACK else BLACK


def get_pieces_hash(board):
    if board is None:
        return -1337

    return hash(json.dumps(sorted(board['pieces'].items())))

def get_piece_moves(board, position):
    '''
    1. By rules ( + on board)
    2. Do not pass someone on the way, except finish with opposite color
    3. Do not make own king under check

    ???
    1. on passan
    2. pawn 8-th rank in different pieces
    3. 0-0 | 0-0-0
    '''
    pieces = board['pieces']
    piece, move_color = pieces[position]

    moves = []
    if piece != 'pawn':
        moves = MOVES[piece]
    else:
        opp_move_color = get_opp_color(move_color)

        if move_color == board['move_up_color']:
            sign = -1
        else:
            sign = 1

        promote_pieces = []
        if position[1] + sign in [0, 7]:
            # Last rank
            for piece in PIECES:
                if piece not in ['king', 'pawn']:
                    promote_pieces.append(piece)
        else:
            promote_pieces.append(None)

        for promote_piece in promote_pieces:
            # First on side
            for x in [-1, 1]:
                new_position = (position[0] + x, position[1] + sign)
                if (new_position in pieces and
                        pieces[new_position][1] == opp_move_color):
                    moves.append([(x, sign, promote_piece)])

            # Second move forward
            # Check if position is empty, to avoid treating as take
            if (position[0], position[1] + sign) not in pieces:
                forward_moves = [(0, sign, promote_piece)]
                if ((position[0], position[1] + 2 * sign) not in pieces and
                        position[1] - sign in [0, 7]):
                    # Move on two steps
                    forward_moves.append((0, 2 * sign, promote_piece))

                moves.append(forward_moves)

    return moves
