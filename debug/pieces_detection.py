import json
import random
import sys
from collections import defaultdict

from board_detection import get_lt_screen_cell_size, get_screen_bitmap, get_pixel, \
    show_image, similiar_pixel, get_settings
from utils import cell_name
from mocks import get_mock


if __name__ == '__main__':
    mode = sys.argv[1]
    settings = get_settings(mode)

    lt_screen, cell_size = get_lt_screen_cell_size(mode)
    if cell_size != settings['cell_size']:
        raise ValueError(
            'Not a valid cell size, actual - {}, required - {}'.format(cell_size, settings['cell_size']))

#     xi = lt_screen[0] * 2
#     yi = lt_screen[1] * 2
#     show_image((xi, yi), (xi + cell_size * 8 * 2, yi + cell_size * 8 * 2))
#     raise

    bitmap_width = cell_size * 8
    bitmap_height = cell_size * 8
    bitmap = get_screen_bitmap(lt_screen, (bitmap_width, bitmap_height))

    for (c, r) in [(5, 2), (6, 0)]:
        pixel = get_pixel(bitmap, c * cell_size * 2 + 1, (7 - r) * cell_size * 2 + 1)
        print [c * 255 for c in pixel]

    cells = [(0, 1), (0, 6)]
    for c in xrange(5):
        cells.append((c, 0))
        cells.append((c, 7))
    stats = defaultdict(dict)
    for cell in cells:
        x = cell[0] * cell_size * 2
        y = (7 - cell[1]) * cell_size * 2
        for dx in xrange(cell_size * 2):
            for dy in xrange(cell_size * 2):
                pixel = get_pixel(bitmap, x + dx, y + dy)
                stats[cell][(dx, dy)] = pixel 

    pixels = {}
    init_board = get_mock(1)
    pixels = {}
    for cell in cells:
        print
        piece, color = init_board.pieces[cell]
        print piece, color
        while True:
            p1 = random.choice(stats[cell].keys())
            p2 = random.choice(stats[cell].keys())

            p1_color = None
            p2_color = None
            for piece_color in ['white_piece', 'black_piece']:
                if similiar_pixel(stats[cell][p1], [settings['colors'][piece_color]]):
                    p1_color = piece_color
                if similiar_pixel(stats[cell][p2], [settings['colors'][piece_color]]):
                    p2_color = piece_color

            if (p1_color and
                    p2_color):
                for cell_2 in cells:
                    if cell == cell_2:
                        continue
    
                    if (stats[cell_2][p1] == stats[cell][p1] and
                            stats[cell_2][p2] == stats[cell][p2]):
                        break
                else:
                    print p1, stats[cell][p1]
                    print p2, stats[cell][p2]
                    pixels.setdefault(piece, {})
                    pixels[piece][color] = []

                    pixels[piece][color].append((p1, p1_color))
                    pixels[piece][color].append((p2, p2_color))
                    break

    print json.dumps(pixels)
