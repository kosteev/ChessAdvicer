import os
import time
from collections import defaultdict

import pyscreenshot
import termcolor

from analyze import dfs
from pieces import PIECES, COLORS, WHITE, BLACK, BOARD_COLORDS, equal_count, MOVE_UP_COLOR
from utils import get_pieces_eval, cell_name, get_pieces_hash


# 1. TODO: (kosteev) Optimize get_board


def get_board():
    white = (239, 217, 183)
    white2 = (238, 216, 185)

    im = pyscreenshot.grab()
    im.load()

    xy_min = None

    #stats = defaultdict(int)
    for x in xrange(im.width):
        for y in xrange(im.height):
            r, g, b, _ = im.im.getpixel((x, y))
            #stats[(r, g, b)] += 1
            if (r, g, b) in [white, white2]:
                if (xy_min is None 
                        or xy_min > (x, y)):
                    xy_min = (x, y)
            if xy_min:
                break
        if xy_min:
                break

    #print sorted(stats.items(), key=lambda x: x[1])[-5:]
    if not xy_min:
        return None

    xy_max = (xy_min[0] + 8 * 128, xy_min[1] + 8 * 128)

    im = im.crop(list(xy_min) + list(xy_max))

    return im


def get_pieces(board):
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

    return pieces


def print_board(pieces):
    for y in xrange(8):
        line = ''
        for x in xrange(8):
            p = pieces.get((x, y))
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
    pieces = None
    if board:
        pieces = get_pieces(board)

    new_hash = get_pieces_hash(pieces)
    if prev_hash == new_hash:
        continue
    prev_hash = new_hash

    if pieces:
        os.system('clear')
        print 'Iteration: {}'.format(iteration)

        print_board(pieces)
        init_eval = get_pieces_eval(pieces)

        print
        print 'Evaluation: {}'.format(init_eval)

        data = {
            'nodes': 0
        }
        moves, evaluation = dfs(pieces, MOVE_UP_COLOR, data)
        print 'Nodes = {}'.format(data['nodes'])

        if not moves:
            print 'No move', evaluation
        else:
            print 'eval: {}'.format(evaluation) 
            for move in moves:
                print '{} -> {}'.format(cell_name(move[0]), cell_name(move[1]))
    else:
        print 'No board found'
    print
    print
