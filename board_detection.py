from collections import defaultdict

from PIL import ImageGrab

from pieces import WHITE, BLACK, PIECES, get_opp_color
from board import Board


CELL_SIZE = 128


COLORS = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'white_board': (239, 216, 183),
    'yellow_white_board': (206, 209, 113),
    'yellow_black_board': (170, 161, 67)
}


def similiar_pixel(p1, colors):
    for color in colors:
        if (abs(p1[0] - color[0]) < 2 and
            abs(p1[1] - color[1]) < 2 and
                abs(p1[2] - color[2]) < 2):
            return True

    return False


def get_board_data():
    im = ImageGrab.grab()
    im.load()

    # Determine top-left corner of board
    xy_min = None
    for x in xrange(im.width):
        for y in xrange(im.height):
            lt_pixel = im.im.getpixel((x, y))
            if similiar_pixel(
                    lt_pixel, [COLORS['white_board'], COLORS['yellow_white_board']]):
                # left-top corner pixel is not our, should move 2 points up
                xy_min = (x, y - 2)
                xy_max = (xy_min[0] + 8 * CELL_SIZE, xy_min[1] + 8 * CELL_SIZE)

                # Check right bottom pixel
                # right-bottom corner pixel is not our, should move 2 points up
                try:
                    rb_pixel = im.im.getpixel((xy_max[0] - 1, xy_max[1] - 3))
                except IndexError:
                    return None
                if not similiar_pixel(
                        rb_pixel, [COLORS['white_board'], COLORS['yellow_white_board']]):
                    # Not a board
                    return None

                break

        if xy_min:
                break

    if not xy_min:
        return None

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
        print 'Can not determine move up color'
        return None

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

    pieces = {}
    move_color = None
    yellow_cells = []
    for c in xrange(8):
        for r in xrange(8):
            x = c * CELL_SIZE
            y = r * CELL_SIZE

            for piece, info in PIECES.items():
                for ind, color in enumerate([WHITE, BLACK]):
                    for pixel_info in info['pixels'][ind]:
                        px = pixel_info[0]
                        py = pixel_info[1]
                        pixel = board_image.im.getpixel((x + px, y + py))
                        if pixel[:-1] != COLORS[pixel_info[-1]]:
                            break
                    else:
                        pieces[(c, r)] = (piece, color)

            # Determine whose move
            pixel = board_image.im.getpixel((x + 5, y + 5))
            if pixel[:-1] in [COLORS['yellow_white_board'], COLORS['yellow_black_board']]:
                yellow_cells.append((c, r))
                if (c, r) in pieces:
                    move_color = get_opp_color(pieces[(c, r)][1])

    move_up_color = board_data['move_up_color']
    if move_color is None:
        if not yellow_cells:
            # Initial position
            move_color = WHITE
        elif (len(yellow_cells) == 2 and
                yellow_cells[0][1] == 0 and yellow_cells[1][1] == 0):
            move_color = move_up_color
        elif (len(yellow_cells) == 2 and
                yellow_cells[0][1] == 7 and yellow_cells[1][1] == 7):
            move_color = get_opp_color(move_up_color)
        else:
            print 'Can not determine move color'
            return None

    return Board(
        pieces=pieces,
        move_up_color=move_up_color,
        move_color=move_color,
        xy=board_data['xy']
    )
