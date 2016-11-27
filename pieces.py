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
