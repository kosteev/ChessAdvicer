import os
import psutil
import random
import sys
import time

from advicer import run_advicer
from board_detection import get_board
from evaluation import take_evaluation
from gui import make_move
from utils import print_board, moves_stringify
from mocks import get_mock


def print_take_evaluation(board):
    s = time.time()
    take_eval = take_evaluation(board)
    e = time.time()
    print
    print 'Time = {:.6f}, nodes = {}'.format(e - s, take_eval['stats']['nodes'])
    print 'Longest seq = {}'.format(
        moves_stringify(take_eval['stats']['longest_moves'], board.move_color))
    print 'Take evaluation: {} ({})'.format(
        take_eval['result']['evaluation'], moves_stringify(
            take_eval['result']['moves'], board.move_color), moves_stringify(
            take_eval['stats']['longest_moves'], board.move_color))


if __name__ == '__main__':
    mode = sys.argv[1]
    max_deep = int(sys.argv[2])
    lines = int(sys.argv[3])
    play = len(sys.argv) > 4 and (sys.argv[4] == '1')

    iteration = 0
    prev_hash = None
    first_line = None
    board = None
    while True:
        # Should be in the beginning (continue issue)
        time.sleep(0.020)
        iteration += 1

        s = time.time()
        # board = get_board(mode, board)
        board = get_mock(2)
        e = time.time()

        new_hash = board.hash if board else -1337
        if prev_hash == new_hash:
            continue
        prev_hash = new_hash

        if board:
            os.system('clear')
            process = psutil.Process(os.getpid())
            print 'Memory usage: {}mb'.format(process.memory_info().rss / 1000 / 1000)
            print 'Time: {:.3f}'.format(e - s)
            print 'Iteration: {}'.format(iteration)
            print 'Max deep: {}'.format(max_deep)
            print 'Lines: {}'.format(lines)
            print 'Play: {}'.format(play)
            print

            print_board(board)
            move_up_color = board.move_up_color
            move_color = board.move_color
            print

            print '{} goes up'.format(move_up_color.upper())
            print '{} to move'.format(move_color.upper())
            print 'Evaluation: {}'.format(board.evaluation)
            # print_take_evaluation(board)
            print

            if (play and
                    move_color != move_up_color):
                print 'Waiting for opponent move'
                continue

            prev_first_line = first_line
            start_time = time.time()
            first_line = run_advicer(
                mode=mode,
                max_deep=max_deep,
                lines=lines,
                play=play,
                board=board
            )
            spent_time = time.time() - start_time

            if play:
                moves = first_line['moves']
                if moves:
                    move = moves[-1]
                    if move['captured_piece']:
                        # Try to humanize `addy`, sleep if needed
                        prev_moves = None
                        if prev_first_line is not None:
                            prev_moves = prev_first_line['moves']

                        unexpected = False
                        if prev_moves is None:
                            print 'No previous calculations'
                            unexpected = True
                        elif (len(prev_moves) < 3 or
                             prev_moves[-3]['position'] != move['position'] or
                             prev_moves[-3]['new_position'] != move['new_position']):
                            # Check only (position, new_position) to reduce count of times it happens
                            print 'Unxepected line, expected: {}'.format(
                                moves_stringify(prev_moves, board.move_color))
                            unexpected = True

                        if unexpected:
                            # If capture and not expected line before
                            # move_time = 0.5 + random.random() * 0.5
                            move_time = 0.85 + random.random() * 0.2
                            time_to_sleep = max(move_time - spent_time, 0)
                            print 'Sleeping (human unexpected case): {:.3f}'.format(time_to_sleep)
                            time.sleep(time_to_sleep)

                    print 'Make a move'
                    make_move(board, move['position'], move['new_position'])
                else:
                    print 'No moves'
        else:
            print 'No board found'
        print
