import os
import psutil
import sys
import time

from advicer import run_advicer
from board_detection import get_board
from evaluation import take_evaluation
from utils import print_board, moves_stringify


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
    analysis = None
    board = None
    while True:
        # Should be in the beginning (continue issue)
        time.sleep(0.020)
        iteration += 1

        s = time.time()
        board = get_board(mode, board)
        # board = get_mock(2)
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

            analysis = run_advicer(
                mode=mode,
                max_deep=max_deep,
                lines=lines,
                play=play,
                board=board,
                prev_analysis=analysis
            )
        else:
            print 'No board found'
        print
