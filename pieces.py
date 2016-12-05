WHITE = 'white'
BLACK = 'black'
COLORS = [WHITE, BLACK]


def get_opp_color(color):
    return WHITE if color == BLACK else BLACK


def on_board((c, r)):
    return 0 <= c < 8 and 0 <= r < 8


PIECES = {
    'rook': {
        'lichess_pixels': [[(30, 38, 'black')], [(33, 29, 'black')]],
        'value': 5,
        'title': 'R',
    },
    'knight': {
        'lichess_pixels': [[(23, 72, 'black')], [(19, 75, 'black')]],
        'value': 3,
        'title': 'N',
    },
    'bishop': {
        'lichess_pixels': [[(21, 107, 'white')], [(20, 107, 'black')]],
        'value': 3,
        'title': 'B',
    },
    'queen': {
        'lichess_pixels': [[(11, 29, 'black')], [(13, 32, 'black')]],
        'value': 9,
        'title': 'Q',
    },
    'king': {
        'lichess_pixels': [[(16, 58, 'black')], [(91, 51, 'black')]],
        'value': 100,
        'title': 'K',
    },
    'pawn': {
        'lichess_pixels': [[(33, 108, 'white')], [(63, 55, 'black'), (95, 113, 'black')]],
        'value': 1,
        'title': 'P',
    }
}


# Valid piece moves by rules
DIFFS = {}
DIFFS['rook'] = [
    [(0, x, None) for x in xrange(1, 8)],
    [(0, -x, None) for x in xrange(1, 8)],
    [(x, 0, None) for x in xrange(1, 8)],
    [(-x, 0, None) for x in xrange(1, 8)]
]
DIFFS['bishop'] = [
    [(x, x, None) for x in xrange(1, 8)],
    [(x, -x, None) for x in xrange(1, 8)],
    [(-x, x, None) for x in xrange(1, 8)],
    [(-x, -x, None) for x in xrange(1, 8)]
]
DIFFS['queen'] = DIFFS['rook'] + DIFFS['bishop']
DIFFS['king'] = [
    [(x, y, None)]
    for x in xrange(-1, 2)
    for y in xrange(-1, 2)
    if x != 0 or y != 0
]
DIFFS['knight'] = [
    [(s1 * x, s2 * (3-x), None)]
    for x in xrange(1, 3)
    for s1 in [-1, 1]
    for s2 in [-1, 1]
]


# Valid piece moves by rules + on board
PROBABLE_MOVES = {}
for piece in DIFFS:
    PROBABLE_MOVES[piece] = {}
    for c in xrange(8):
        for r in xrange(8):
            PROBABLE_MOVES[piece][(c, r)] = []
            for variant in DIFFS[piece]:
                moves_variant = []
                for diff in variant:
                    move = (c + diff[0], r + diff[1], None)
                    if not on_board(move[:-1]):
                        break

                    moves_variant.append(move)

                if moves_variant:
                    PROBABLE_MOVES[piece][(c, r)].append(moves_variant)
