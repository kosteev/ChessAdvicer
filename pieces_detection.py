import json
import random
from collections import defaultdict

from board_detection import get_lt_screen_cell_size, get_screen_bitmap, get_pixel, \
    show_image, similiar_pixel, COLORS, CELL_SIZE
from utils import cell_name


if __name__ == '__main__':
    lt_screen, cell_size = get_lt_screen_cell_size(None)
    if cell_size != CELL_SIZE:
        raise ValueError(
            'Not a valid cell size, actual - {}, required - {}'.format(cell_size, CELL_SIZE))

#     xi = lt_screen[0] * 2
#     yi = lt_screen[1] * 2
#     show_image((xi, yi), (xi + cell_size * 8 * 2, yi + cell_size * 8 * 2))
#     raise

    bitmap_width = cell_size * 8
    bitmap_height = cell_size * 8
    bitmap = get_screen_bitmap(lt_screen, (bitmap_width, bitmap_height))

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
    for cell in cells:
        print
        print cell_name(cell)
        while True:
            p1 = random.choice(stats[cell].keys())
            p2 = random.choice(stats[cell].keys())
            if (similiar_pixel(stats[cell][p1], [COLORS['white_piece'], COLORS['black_piece']])
                    and similiar_pixel(stats[cell][p2], [COLORS['white_piece'], COLORS['black_piece']])):
                for cell_2 in cells:
                    if cell == cell_2:
                        continue
    
                    if (stats[cell_2][p1] == stats[cell][p1] and
                            stats[cell_2][p2] == stats[cell][p2]):
                        break
                else:
                    print p1, stats[cell][p1]
                    print p2, stats[cell][p2]
                    break
