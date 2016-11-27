import sys


WHITE = 'white'
BLACK = 'black'
COLORS = [WHITE, BLACK]


def get_opp_color(color):
    return WHITE if color == BLACK else BLACK


PIECES = {
    'rook': {
        'count': [2022, 4196],
        'value': 5,
        'priority': 5,
        'title': 'R',
    },
    'knight': {
        'count': [1515, 5312],
        'value': 3,
        'priority': 3,
        'title': 'N',
    },
    'bishop': {
        'count': [1789, 3571],
        'value': 3,
        'priority': 3,
        'title': 'B',
    },
    'queen': {
        'count': [2942, 4593],
        'value': 9,
        'priority': 9,
        'title': 'Q',
    },
    'king': {
        'count': [1854, 3590],
        'value': 100,
        'priority': 0,
        'title': 'K',
    },
    'pawn': {
        'count': [912, 3867],
        'value': 1,
        'priority': 9,
        'title': 'P',
    }
}


PIECE_TOLERANCE = 8


# check tolerance
counts_w = []
counts_b = []
for piece in PIECES.values():
    counts_w.append(piece['count'][0])
    counts_b.append(piece['count'][1])


def check_counts(counts):
    min_t = sys.maxint
    for ind_1 in xrange(len(counts)):
        for ind_2 in xrange(ind_1):
            min_t = min(min_t, abs(counts[ind_1] - counts[ind_2]))
    assert min_t > PIECE_TOLERANCE * 2


check_counts(counts_w + counts_b)


def equal_count(v1, v2):
    return abs(v1 - v2) <= PIECE_TOLERANCE


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


def get_piece_moves(board, position):
    '''
    1. By rules ( + on board)
    2. Do not pass someone on the way, except finish with opposite color
    3. Do not make own king under check

    ???
    1. on passan
    2. 0-0 | 0-0-0
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
