WHITE = 'white'
BLACK = 'black'
COLORS = [WHITE, BLACK]

def get_opp_color(color):
    return WHITE if color == BLACK else BLACK


WHITE_KC, WHITE_QC, BLACK_KC, BLACK_QC = range(4)

def get_castles(white_kc=False, white_qc=False, black_kc=False, black_qc=False):
    return [white_kc, white_qc, black_kc, black_qc]

def get_castle_id(color, t):
    d = {
         (WHITE, 'k'): WHITE_KC,
         (WHITE, 'q'): WHITE_QC,
         (BLACK, 'k'): BLACK_KC,
         (BLACK, 'q'): BLACK_QC
    }
    return d[(color, t)]


def on_board((c, r)):
    return 0 <= c < 8 and 0 <= r < 8


PIECES = {
    'rook': {
        'value': 5,
        'title': 'R',
    },
    'knight': {
        'value': 3,
        'title': 'N',
    },
    'bishop': {
        'value': 3,
        'title': 'B',
    },
    'queen': {
        'value': 9,
        'title': 'Q',
    },
    'king': {
        'value': 100,
        'title': 'K',
    },
    'pawn': {
        'value': 1,
        'title': 'P',
    }
}


def get_piece_by_title(title):
    for piece, piece_info in PIECES.items():
        if piece_info['title'].lower() == title.lower():
            return piece

    return None


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


# Valid piece moves by rules + on board (all except pawns)
PROBABLE_MOVES = {}
for piece in DIFFS:
    PROBABLE_MOVES[piece] = {}
    for c in xrange(8):
        for r in xrange(8):
            PROBABLE_MOVES[piece][(c, r)] = []
            for variant in DIFFS[piece]:
                moves_variant = []
                for diff in variant:
                    move = {
                        'new_position': (c + diff[0], r + diff[1])
                    }
                    if not on_board(move['new_position']):
                        break

                    moves_variant.append(move)

                if moves_variant:
                    PROBABLE_MOVES[piece][(c, r)].append(moves_variant)

PIECE_CELL_VALUE = {}
for piece in PROBABLE_MOVES:
    PIECE_CELL_VALUE[piece] = {}
    for cell in PROBABLE_MOVES[piece]:
        if piece == 'king':
            value = 0
        else:
            value = sum(
                len(v) for v in PROBABLE_MOVES[piece][cell])
        PIECE_CELL_VALUE[piece][cell] = value

PIECE_CELL_VALUE['pawn'] = {}
for c in xrange(8):
    for r in xrange(1, 7):
        PIECE_CELL_VALUE['pawn'][(c, r)] = 1 if c in [0, 7] else 2

# For all pieces, except pawn and king
BEAT_VARIANTS = [{
    'line': [(x, 0) for x in xrange(1, 8)],
    'pieces': ['rook', 'queen']
}, {
    'line': [(-x, 0) for x in xrange(1, 8)],
    'pieces': ['rook', 'queen']
}, {
    'line': [(0, x) for x in xrange(1, 8)],
    'pieces': ['rook', 'queen']
}, {
    'line': [(0, -x) for x in xrange(1, 8)],
    'pieces': ['rook', 'queen']
}]
for s1 in [-1, 1]:
    for s2 in [-1, 1]:
        BEAT_VARIANTS.append({
            'line': [(s1 * x, s2 * x) for x in xrange(1, 8)],
            'pieces': ['bishop', 'queen']
        })
        for x in xrange(1, 3):
            BEAT_VARIANTS.append({
                'line': [(s1 * x, s2 * (3-x))],
                'pieces': ['knight']
            })

BEAT_LINES = {}
for color in [WHITE, BLACK]:
    sign = -1 if color == WHITE else 1
    BEAT_LINES[color] = {}
    for c in xrange(8):
        for r in xrange(8):
            cell = (c, r)
            BEAT_LINES[color][cell] = []
            for variant in BEAT_VARIANTS:
                line_pieces = []
                for diff in variant['line']:
                    beaten_cell = (c + diff[0], r + diff[1])
                    if not on_board(beaten_cell):
                        break

                    additional_pieces = []
                    # Extra logic for pawns
                    if (abs(diff[0]) == 1 and
                            diff[1] == sign):
                        additional_pieces += ['pawn']
                    # Extra logic for kings
                    if (abs(diff[0]) <= 1 and
                            abs(diff[1]) <= 1):
                        additional_pieces += ['king']
                    line_pieces.append({
                        'cell': beaten_cell,
                        'pieces': variant['pieces'] + additional_pieces
                    })
                if line_pieces:
                    BEAT_LINES[color][cell].append(line_pieces)
