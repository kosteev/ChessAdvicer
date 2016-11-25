import os
import time

from analyze import dfs
from utils import get_pieces_eval, get_pieces_hash, format_move, make_move, get_board, \
    print_board


# 1. TODO: (kosteev) Optimize get_board


iteration = 0
prev_hash = None
while True:
    inp = raw_input('Make a move?')

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
        move_up_color = board['move_up_color']
        init_eval = get_pieces_eval(board, move_up_color)

        print
        print '{} goes up'.format(move_up_color.upper())
        print 'Evaluation: {}'.format(init_eval)

        data = {
            'nodes': 0
        }
        result = dfs(board, move_up_color, data, lines=5)
        print 'Nodes = {}'.format(data['nodes'])

        for ind, line in enumerate(result):
            print '{}. ({}) {}'.format(
                ind + 1, line[0],
                '; '.join(
                    [format_move(move, move_up_color)
                     for move in reversed(line[1])]))
        move = result[0][1][-1]
        make_move(board, move['position'], move['new_position'])
    else:
        print 'No board found'
    print
    print
