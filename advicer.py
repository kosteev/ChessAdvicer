import os
import sys
import time

from analyze import Analyzer
from board_detection import get_board
from gui import make_move
from utils import get_pieces_eval, get_pieces_hash, format_move, print_board


# 2minutes - deep=3
# 3minutes - deep=4


if __name__ == '__main__':
    # ...
    max_deep = int(sys.argv[1])
    lines = int(sys.argv[2])
    play = len(sys.argv) > 3 and (sys.argv[3] == '1')
    analyzer = Analyzer(max_deep=max_deep, lines=lines)

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
            print 'Lines: {}'.format(lines)
            print 'Play: {}'.format(play)
            print

            print_board(board)
            move_up_color = board.move_up_color
            move_color = board.move_color
            init_eval = get_pieces_eval(board)
            print

            print '{} goes up'.format(move_up_color.upper())
            print '{} to move'.format(move_color.upper())
            print 'Evaluation: {}'.format(init_eval)
            print

            if move_color != move_up_color:
                print 'Waiting for opponent move'
                continue

            print 'Calculating lines...'

            data = {
                'nodes': 0
            }
            # TODO: (kosteev) write in the process of dfs working
            start_time = time.time()
            result = analyzer.dfs(
                board, move_color, data)
            end_time = time.time()

            print 'Time = {:.3}, nodes = {}'.format(end_time - start_time, data['nodes'])

            for ind, line in enumerate(result):
                print '{}. ({}) {}'.format(
                    ind + 1, line['evaluation'],
                    '; '.join(
                        [format_move(move, move_up_color)
                         for move in reversed(line['moves'])]))

            if play:
                moves = result[0]['moves']
                if moves:
                    move = moves[-1]
                    make_move(board, move['position'], move['new_position'])
                else:
                    print 'No moves'
        else:
            print 'No board found'
        print
        print
