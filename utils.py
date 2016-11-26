import json
from collections import defaultdict

import pyautogui
import pyscreenshot
import termcolor

from pieces import PIECES, WHITE, BLACK, equal_count, BOARD_COLORS


CELL_SIZE = 128


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


def focus_board(board):
    x = board['xy'][0] - 10
    y = board['xy'][1] - 10

    pyautogui.click(x / 2, y / 2)


def click_cell(board, position):
    x = board['xy'][0] + (position[0] + 0.5) * CELL_SIZE
    y = board['xy'][1] + (position[1] + 0.5) * CELL_SIZE

    pyautogui.click(x / 2, y / 2)


def make_move(board, position, new_position):
    # original_position = pyautogui.position()

    focus_board(board)
    click_cell(board, position)
    click_cell(board, new_position)

    # pyautogui.click(original_position)


WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
WHITE_BOARD_COLOR = (239, 217, 183)
YELLOW_WHITE_BOARD_COLOR = (206, 209, 113)
YELLOW_BLACK_BOARD_COLOR = (170, 161, 67)

def get_board_data():
    im = pyscreenshot.grab()
    im.load()

    xy_min = None

    #stats = defaultdict(int)
    for x in xrange(im.width):
        for y in xrange(im.height):
            r, g, b, _ = im.im.getpixel((x, y))
            #stats[(r, g, b)] += 1
            if (r, g, b) in [WHITE_BOARD_COLOR, YELLOW_WHITE_BOARD_COLOR]:
                if (xy_min is None or
                        xy_min > (x, y)):
                    xy_min = (x, y)
            if xy_min:
                break
        if xy_min:
                break

    if not xy_min:
        return None

    # left-top corner pixel is not our
    xy_min = xy_min[0], xy_min[1] - 2
    xy_max = (xy_min[0] + 8 * CELL_SIZE, xy_min[1] + 8 * CELL_SIZE)

    # Determine orientation
    or_xy_min = (xy_min[0] + 3 * CELL_SIZE + CELL_SIZE / 2 - 10, xy_max[1] + 5)
    or_xy_max = (or_xy_min[0] + 20, or_xy_min[1] + 22)

    or_im = im.crop(list(or_xy_min) + list(or_xy_max))
    stats = defaultdict(int)
    for x in xrange(or_im.width):
        for y in xrange(or_im.height):
            r, g, b, _ = or_im.im.getpixel((x, y))
            stats[(r, g, b)] += 1

    move_up_color = None
    grey = (137, 137, 137)
    if abs(stats[grey] - 84) < 5:
        # D - 84
        move_up_color = WHITE
    else:
        # E - 59
        move_up_color = BLACK

    board_image = im.crop(list(xy_min) + list(xy_max))

    return {
        'board_image': board_image,
        'xy': xy_min,
        'move_up_color': move_up_color
    }


def get_board():
    board_data = get_board_data()
    if not board_data:
        return None

    board_image = board_data['board_image']

    size = (board_image.width + 4) / 8 # round to nearest integer

    stats = defaultdict(lambda: defaultdict(int))
    for x in xrange(board_image.width):
        for y in xrange(board_image.height):
            cell = (x / size, y / size)
            pixel = board_image.im.getpixel((x, y))

            stats[cell][(pixel[0], pixel[1], pixel[2])] += 1

    move_color = None
    yellow_r = None
    pieces = {}
    for c in xrange(8):
        for r in xrange(8):
            cell_info = stats[(c, r)]
            for piece_name, info in PIECES.items():
                if equal_count(cell_info[BLACK_COLOR], info['count'][0]):
                    pieces[(c, r)] = (piece_name, WHITE)
                elif equal_count(cell_info[BLACK_COLOR], info['count'][1]):
                    pieces[(c, r)] = (piece_name, BLACK)

            # Determine whose move
            if (cell_info[YELLOW_WHITE_BOARD_COLOR] or
                    cell_info[YELLOW_BLACK_BOARD_COLOR]):
                yellow_r = r
                if (c, r) in pieces:
                    move_color = get_opp_color(pieces[(c, r)][1])

    move_up_color = board_data['move_up_color']
    if move_color is None:
        if yellow_r is None:
            # Initial position
            move_color = WHITE
        elif yellow_r == 0:
            move_color = move_up_color
        elif yellow_r == 7:
            move_color = get_opp_color(move_up_color)
        else:
            # !!!!!!!!!!!!!
            board_image.show()
            raise Exception('Can not determine move color')

    return {
        'xy': board_data['xy'],
        'pieces': pieces,
        'move_up_color': move_up_color,
        'move_color': move_color
    }


def print_board(board):
    for y in xrange(8):
        line = ''
        for x in xrange(8):
            p = board['pieces'].get((x, y))
            if p is None:
                line += '.'
            else:
                line += termcolor.colored(PIECES[p[0]]['title'], BOARD_COLORS[p[1]])
        print line


def get_move_color(board):
    move_up_color = board['move_up_color']
    move_color = get_opp_color(move_up_color)  # By default
    for position, (_, color) in board['pieces'].items():
        if color != move_up_color:
            continue

        focus_board(board)
        click_cell(board, position)
        break

    return move_color