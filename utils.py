import json

from pieces import PIECES, MOVE_UP_COLOR, WHITE, BLACK


MOVES = {}
MOVES['rook'] = [
    [(0, x) for x in xrange(1, 8)],
    [(0, -x) for x in xrange(1, 8)],
    [(x, 0) for x in xrange(1, 8)],
    [(-x, 0) for x in xrange(1, 8)]
]
MOVES['bishop'] = [
    [(x, x) for x in xrange(1, 8)],
    [(x, -x) for x in xrange(1, 8)],
    [(-x, x) for x in xrange(1, 8)],
    [(-x, -x) for x in xrange(1, 8)]
]
MOVES['queen'] = MOVES['rook'] + MOVES['bishop']
MOVES['king'] = [
    [(x, y)]
    for x in xrange(-1, 2)
    for y in xrange(-1, 2)
    if x != 0 or y != 0
]
MOVES['knight'] = [
    [(s1 * x, s2 * (3-x))]
    for x in xrange(1, 3)
    for s1 in [-1, 1]
    for s2 in [-1, 1]
]


MAX_EVALUATION = 1000


def get_pieces_eval(pieces):
    '''
    pieces = {(1, 2): ('rook', 'white)}
    '''
    total = 0
    for (piece, color) in pieces.values():
        if color == MOVE_UP_COLOR:
            total += PIECES[piece]['value']
        else:
            total -= PIECES[piece]['value']

    return total


def cell_name(cell):
    if MOVE_UP_COLOR == WHITE:
        return '{}{}'.format(chr(ord('a') + cell[0]), 8 - cell[1])
    else:
        return '{}{}'.format(chr(ord('h') - cell[0]), cell[1] + 1)


def get_opp_color(color):
    return WHITE if color == BLACK else BLACK


def get_pieces_hash(pieces):
    if pieces is None:
        return -1137

    return hash(json.dumps(sorted(pieces.items())))

def get_piece_moves(pieces, position):
    '''
    1. By rules ( + on board)
    2. Do not pass someone on the way, except finish with opposite color
    3. Do not make own king under check

    ???
    1. on passan
    2. pawn 8-th rank
    3. 0-0 | 0-0-0
    '''
    piece, move_color = pieces[position]

    moves = []
    if piece != 'pawn':
        moves = MOVES[piece]
    else:
        opp_move_color = get_opp_color(move_color)

        if move_color == MOVE_UP_COLOR:
            sign = -1
        else:
            sign = 1

        # First on side
        for x in [-1, 1]:
            new_position = (position[0] + x, position[1] + sign)
            if (new_position in pieces
                    and pieces[new_position][1] == opp_move_color):
                moves.append([(x, sign)])

        # Second move forward
        if (position[0], position[1] + sign) not in pieces:
            forward_moves = [(0, sign)]
            if ((position[0], position[1] + 2 * sign) not in pieces and
                    position[1] - sign in [0, 7]):
                # Move on two steps
                forward_moves.append((0, 2 * sign))
            moves.append(forward_moves)

    return moves
