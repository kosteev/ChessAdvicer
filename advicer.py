import os
import time
from collections import defaultdict

import pyscreenshot
import termcolor

from analyze import dfs
from pieces import PIECES, WHITE, BLACK, BOARD_COLORDS, equal_count
from utils import get_pieces_eval, get_pieces_hash, format_move


# 1. TODO: (kosteev) Optimize get_board


def get_board_image():
    white = (239, 217, 183)
    yellow = (206, 209, 113)

    im = pyscreenshot.grab()
    im.load()

    xy_min = None

    #stats = defaultdict(int)
    for x in xrange(im.width):
        for y in xrange(im.height):
            r, g, b, _ = im.im.getpixel((x, y))
            #stats[(r, g, b)] += 1
            if (r, g, b) in [white, yellow]:
                if (xy_min is None 
                        or xy_min > (x, y)):
                    xy_min = (x, y)
            if xy_min:
                break
        if xy_min:
                break

    if not xy_min:
        return None, None

    xy_max = (xy_min[0] + 8 * 128, xy_min[1] + 8 * 128)

    or_xy_min = (xy_min[0] + 3 * 128 + 128 / 2 - 10, xy_max[1] + 5)
    or_xy_max = (or_xy_min[0] + 20, or_xy_min[1] + 20)

    or_im = im.crop(list(or_xy_min) + list(or_xy_max))
    stats = defaultdict(int)
    for x in xrange(or_im.width):
        for y in xrange(or_im.height):
            r, g, b, _ = or_im.im.getpixel((x, y))
            stats[(r, g, b)] += 1

    move_up_color = None
    grey = (137, 137, 137)
    if abs(stats[grey] - 84) < 5:
        # D
        move_up_color = WHITE
    else:
        # E
        move_up_color = BLACK

    im = im.crop(list(xy_min) + list(xy_max))

    return im, move_up_color


def get_board():
    board, move_up_color = get_board_image()
    if not board:
        return None

    board.load()

    size = (board.width + 4) / 8 # round to nearest integer 

    stats_w = defaultdict(int)
    stats_b = defaultdict(int)
    for x in xrange(board.width):
        for y in xrange(board.height):
            cell = (x / size, y / size)
            pixel = board.im.getpixel((x, y))

            if pixel == (255, 255, 255, 255):
                stats_w[cell] += 1

            if pixel == (0, 0, 0, 255):
                stats_b[cell] += 1

    pieces = {}
    for c in xrange(8):
        for r in xrange(8):
            for piece_name, info in PIECES.items():
                if equal_count(stats_b[(c, r)], info['count'][0]):
                    pieces[(c, r)] = (piece_name, WHITE)
                elif equal_count(stats_b[(c, r)], info['count'][1]):
                    pieces[(c, r)] = (piece_name, BLACK)

    return {
        'pieces': pieces,
        'move_up_color': move_up_color
    }


def print_board(board):
    for y in xrange(8):
        line = ''
        for x in xrange(8):
            p = board['pieces'].get((x, y))
            if p is None:
                line += '.'
            else:
                line += termcolor.colored(PIECES[p[0]]['title'], BOARD_COLORDS[p[1]])
        print line


iteration = 0
prev_hash = None
while True:
    # Should be in the beginning (continue issue)
    time.sleep(0.1)
    iteration += 1

    board = get_board()

    new_hash = get_pieces_hash(board)
    if prev_hash == new_hash:
        continue
    prev_hash = new_hash

    if board:
        os.system('clear')
        print 'Iteration: {}'.format(iteration)

        print_board(board)
        init_eval = get_pieces_eval(board)

        print
        print 'Evaluation: {}'.format(init_eval)

        data = {
            'nodes': 0
        }
        result = dfs(board, board['move_up_color'], data, lines=5)
        print 'Nodes = {}'.format(data['nodes'])

        for ind, line in enumerate(result):
            print '{}. ({}) {}'.format(
                ind + 1, line[0],
                '; '.join(
                    [format_move(move, board['move_up_color'])
                     for move in reversed(line[1])]))
    else:
        print 'No board found'
    print
    print
