import os
import psutil
import random
import sys
import time
from collections import defaultdict

from advicer import run_advicer
from board_detection import get_board
from gui import make_move
from utils import print_board, color_sign
from mocks import get_mock
from pieces import WHITE


if __name__ == '__main__':
    mode = sys.argv[1]
    max_deep = int(sys.argv[2])
    lines = int(sys.argv[3])
    play = len(sys.argv) > 4 and (sys.argv[4] == '1')

    board_hashes = defaultdict(int)
    iteration = 0
    prev_hash = None
    first_line = None
    board = None
    total_sleep = 0
    while True:
        # Should be in the beginning (continue issue)
        time.sleep(0.020)
        iteration += 1

        s = time.time()
        board = get_board(mode, board)
        # board = get_mock(17)
        e = time.time()

        new_hash = board.hash if board else -1337
        if prev_hash == new_hash:
            continue
        prev_hash = new_hash

        if board:
            # Collect hashes, can be used by advicer.
            board_hashes[board.hash] += 1

            os.system('clear')
            process = psutil.Process(os.getpid())
            print 'Memory usage: {}mb'.format(process.memory_info().rss / 1000 / 1000)
            print 'Time: {:.3f}'.format(e - s)
            print 'Iteration: {}'.format(iteration)
            analyze_max_deep = max_deep
            # TODO: use len(get_board_moves) or time
            if len(board.pieces) <= 12:
                print 'Max deep increased by 1'
                analyze_max_deep += 1
            print 'Max deep: {}'.format(analyze_max_deep)
            print 'Lines: {}'.format(lines)
            print 'Play: {}'.format(play)
            print

            print_board(board)
            move_up_color = board.move_up_color
            move_color = board.move_color
            sign = color_sign(move_color)
            print

            print '{} goes up'.format(move_up_color.upper())
            print '{} to move'.format(move_color.upper())
            print 'Evaluation: {}'.format(board.evaluation)
            if play:
                print 'Total sleep: {:.3f}'.format(total_sleep)
            print

            if (play and
                    move_color != move_up_color):
                print 'Waiting for opponent move'
                continue

            prev_first_line = first_line
            start_time = time.time()
            first_line = run_advicer(
                mode=mode,
                max_deep=analyze_max_deep,
                lines=lines,
                board=board,
                board_hashes=board_hashes
            )
            spent_time = time.time() - start_time

            if play:
                moves = first_line['moves']
                if moves:
                    move = moves[-1]
                    # Try to humanize `addy`, sleep if needed
                    unexpected = False
                    print
                    if prev_first_line is None:
                        print 'No pre calculations'
                    elif move['captured_piece']:
                        prev_moves = prev_first_line['moves']
                        if (len(prev_moves) < 3 or
                             prev_moves[-3]['position'] != move['position'] or
                             prev_moves[-3]['new_position'] != move['new_position']):
                            # Check only (position, new_position) to reduce count of times it happens
                            print 'Not expected capture'
                            unexpected = True
                    else:
                        # If evaluation changed too much
                        # TODO: check prev_moves???
                        diff = first_line['evaluation'] - prev_first_line['evaluation']
                        tolerance = 0.5
                        if sign * diff > tolerance:
                            print 'Evaluation changed too much: {:.3f}'.format(sign * diff)
                            unexpected = True

                    # By default
                    time_to_sleep = max(0.2 + random.random() * 0.1 - spent_time, 0)
                    if unexpected:
                        move_time = 0.6 + random.random() * 0.4
                        time_to_sleep = max(move_time - spent_time, 0)
                        print 'Unxepected line: sleeping: {:.3f}'.format(time_to_sleep)
                    total_sleep += time_to_sleep
                    time.sleep(time_to_sleep)

                    make_move(board, move['position'], move['new_position'])
                else:
                    print 'No moves'
        else:
            print 'No board found'
        print
