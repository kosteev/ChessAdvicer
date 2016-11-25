import os
import sys
import time

from analyze import dfs
from utils import get_pieces_eval, get_pieces_hash, format_move, make_move, get_board, \
    print_board


if __name__ == '__main__':
    # ...
    max_deep = int(sys.argv[1])
    play = len(sys.argv) > 2 and (sys.argv[2] == '1')

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
            print 'Max deep: {}'.format(max_deep)
            print 'Play: {}'.format(play)
            print

            print_board(board)
            move_up_color = board['move_up_color']
            init_eval = get_pieces_eval(board, move_up_color)
            print

            print '{} goes up'.format(move_up_color.upper())
            print 'Evaluation: {}'.format(init_eval)
            print

            if play:
                move_color = board['move_color']
                if move_color != move_up_color:
                    print 'Waiting for opponent move'
                    continue

            print 'Calculating lines...'

            data = {
                'nodes': 0
            }
            # TODO: (kosteev) write in the process of dfs working
            result = dfs(
                board, move_up_color, data, max_deep, lines=5)
            print 'Nodes = {}'.format(data['nodes'])

            for ind, line in enumerate(result):
                print '{}. ({}) {}'.format(
                    ind + 1, line[0],
                    '; '.join(
                        [format_move(move, move_up_color)
                         for move in reversed(line[1])]))
            if play:
                moves = result[0][1]
                if moves:
                    move = moves[-1]
                    make_move(board, move['position'], move['new_position'])
                else:
                    print 'No moves'
        else:
            print 'No board found'
        print
        print
