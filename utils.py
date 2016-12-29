import termcolor

from pieces import PIECES, WHITE, BLACK, get_castles, WHITE_KC, WHITE_QC, BLACK_KC, BLACK_QC


def color_sign(color):
    '''
    Returns 1 for white and -1 for black.
    Used in many functions, e.g.: get_material_eval
    '''
    return 1 if color == WHITE else -1


def normalize_cell(cell, move_up_color):
    '''
    Normalizes cell relative to a8 square.
    '''
    if move_up_color == BLACK:
        cell = (7 - cell[0], 7 - cell[1])

    return cell


def h_name(cell):
    return cell[1] + 1


def v_name(cell):
    return chr(ord('a') + cell[0])


def name_to_cell(name):
    cell = (ord(name[0]) - ord('a'), int(name[1]) - 1)

    return cell


def cell_name(cell):
    return '{}{}'.format(v_name(cell), h_name(cell))


def format_move(move):
    if (move['piece'] == 'king' and
            abs(move['position'][0] - move['new_position'][0]) == 2):
        # Castles
        if move['new_position'][0] == 6:
            return 'O-O'
        return 'O-O-O'

    if move['piece'] == 'pawn':
        if move['captured_piece']:
            piece_title = v_name(move['position'])
        else:
            piece_title = ''
    else:
        piece_title = PIECES[move['piece']]['title']

    return '{piece_title}{is_take}{new_position}{new_piece_title}{check_mate}'.format(
        piece_title=piece_title,
        is_take='x' if move['captured_piece'] else '',
        new_position=cell_name(move['new_position']),
        new_piece_title=('=' + PIECES[move['new_piece']]['title']) if move['piece'] != move['new_piece'] else '',
        check_mate=''
    )


def moves_stringify(moves, move_color, ind=1):
    if len(moves) == 0:
        return ''

    # !!!
    moves = list(moves)

    result = ''
    if move_color == BLACK:
        result = format_move(moves[-1])
        ind += 1
        moves = moves[:-1]

    while moves:
        move = moves.pop()
        if result:
            result += ' '
        result += '{}.{}'.format(ind, format_move(move))

        if moves:
            move = moves.pop()
            result += ' {}'.format(format_move(move))

        ind += 1

    return result

    return '; '.join(
        [format_move(move)
         for move in reversed(moves)])


def print_board(board):
    BOARD_COLORS = {
        WHITE: 'cyan',
        BLACK: 'grey'
    }

    for r in xrange(7, -1, -1):
        line = ''
        for c in xrange(8):
            cell = (c, r)
            cell = normalize_cell(cell, board.move_up_color)
            p = board.pieces.get(cell)
            if p is None:
                line += '.'
            else:
                line += termcolor.colored(PIECES[p[0]]['title'], BOARD_COLORS[p[1]])
        print line
    print get_fen_from_board(board)


def get_fen_from_board(board):
    fen_1 = []
    for r in xrange(7, -1, -1):
        row = ""
        empty = 0
        for c in xrange(8):
            cell = (c, r)

            if cell in board.pieces:
                if empty:
                    row += str(empty)

                piece, color = board.pieces[cell]
                title = PIECES[piece]['title']
                if color == WHITE:
                    title = title.upper()
                else:
                    title = title.lower()

                row += title
                empty = 0
            else:
                empty += 1
        if empty:
            row += str(empty)

        fen_1.append(row)

    # TODO: provide k/q castles
    castles = ''
    if board.castles[WHITE_KC]:
        castles += 'K'
    if board.castles[WHITE_QC]:
        castles += 'Q'
    if board.castles[BLACK_KC]:
        castles += 'k'
    if board.castles[BLACK_QC]:
        castles += 'q'
    if not castles:
        castles = '-'
    fen = '{} {} {} {} - -'.format(
        '/'.join(fen_1),
        'w' if board.move_color == WHITE else 'b',
        castles,
        cell_name(board.en_passant) if board.en_passant else '-')

    return fen


def get_board_from_fen(fen):
    from board import Board

    p1, p2, p3, p4, _, _ = fen.split(' ')

    board_list = list(reversed(p1.split('/')))
    pieces = {}
    for r in xrange(7, -1, -1):
        c = 0
        for l in board_list[r]:
            if l.isdigit():
                c += int(l)
            else:
                for piece, piece_info in PIECES.items():
                    if piece_info['title'].lower() == l.lower():
                        color = BLACK if l == l.lower() else WHITE
                        pieces[(c, r)] = (piece, color)
                        break
                c += 1

    move_color = WHITE if p2 == 'w' else BLACK

    castles = get_castles(
        white_kc='K' in p3, white_qc='Q' in p3, black_kc='k' in p3, black_qc='q' in p3)

    en_passant = None
    if p4 != '-':
        en_passant = name_to_cell(p4)

    return Board(
        pieces=pieces,
        move_color=move_color,
        en_passant=en_passant,
        castles=castles
    )


def get_color_pieces(pieces, leave_color):
    return {
        position: (piece, color)
        for position, (piece, color) in pieces.items()
        if color == leave_color
    }


def update_castles(castles, positions):
    if ((4, 0) in positions or
            (7, 0) in positions):
        castles[WHITE_KC] = False
    if ((4, 0) in positions or
            (0, 0) in positions):
        castles[WHITE_QC] = False
    if ((4, 7) in positions or
            (7, 7) in positions):
        castles[BLACK_KC] = False
    if ((4, 7) in positions or
            (0, 7) in positions):
        castles[BLACK_QC] = False

    return castles
