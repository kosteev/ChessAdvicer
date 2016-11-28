from collections import defaultdict

from PIL import ImageGrab

from pieces import WHITE, BLACK, PIECES, equal_count, get_opp_color
from board import Board


CELL_SIZE = 128

WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
WHITE_BOARD_COLOR = (239, 216, 183)
YELLOW_WHITE_BOARD_COLOR = (206, 209, 113)
YELLOW_BLACK_BOARD_COLOR = (170, 161, 67)


def get_board_data():
    im = ImageGrab.grab()
    im.load()

    # Determine top-left corner of board
    xy_min = None
    for x in xrange(im.width):
        for y in xrange(im.height):
            r, g, b, _ = im.im.getpixel((x, y))
            for color in [WHITE_BOARD_COLOR, YELLOW_WHITE_BOARD_COLOR]:
                if (abs(color[0] - r) < 2 and
                    abs(color[1] - g) < 2 and
                        abs(color[2] - b) < 2):
                    xy_min = (x, y)
                    break

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
    if abs(stats[grey] - 84) < 1:
        # D - 84
        move_up_color = WHITE
    elif abs(stats[grey] - 59) < 1:
        # E - 59
        move_up_color = BLACK
    else:
        im.show()
        raise Exception('Can not determine move up color')

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

    stats = defaultdict(lambda: defaultdict(int))
    # TODO: (kosteev) could iterate not over all pixels
    for x in xrange(8):
        for y in xrange(8):
            gx = x * CELL_SIZE
            gy = y * CELL_SIZE
            cell = (x, y)
            for px in xrange(CELL_SIZE):
                for py in xrange(CELL_SIZE):
                    pixel = board_image.im.getpixel((gx + px, gy + py))
                    stats[cell][(pixel[0], pixel[1], pixel[2])] += 1

    move_color = None
    yellow_r = None
    pieces = {}
    for c in xrange(8):
        for r in xrange(8):
            cell_info = stats[(c, r)]
            for piece_name, info in PIECES.items():
                if equal_count(get_color_count(cell_info, BLACK_COLOR), info['count'][0]):
                    pieces[(c, r)] = (piece_name, WHITE)
                elif equal_count(get_color_count(cell_info, BLACK_COLOR), info['count'][1]):
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

    return Board(
        pieces=pieces,
        move_up_color=move_up_color,
        move_color=move_color,
        xy=board_data['xy']
    )


def get_deviation_color(color):
    deviation = 1
    for x in xrange(-deviation, deviation + 1):
        for y in xrange(-deviation, deviation + 1):
            for z in xrange(-deviation, deviation + 1):
                yield color[0] + x, color[1] + y, color[2] + z


def get_color_count(stats, color):
    result = 0
    for deviation_color in get_deviation_color(color):
        result += stats[deviation_color]

    return result
