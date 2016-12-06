import os
import random
import sys
import time

from analyze import AlphaBetaAnalyzer
from board_detection import get_board
from evaluation import simple_evaluation
from gui import make_move
from utils import get_pieces_hash, print_board, moves_stringify


def run_analyzer(board, max_deep, lines, move_color):
    min_time = 0.8
    max_time = 1.2
    move_time = min_time + (max_time - min_time) * random.random()
    print move_time

    # TODO: fix bug with time
    analyzer = AlphaBetaAnalyzer(
        max_deep=max_deep, lines=lines, max_time=move_time
    )

    start_time = time.time()
    analysis = analyzer.analyze(board, move_color)
    # Sleep if analyzer was too fast
    to_sleep = max(move_time - (time.time() - start_time), 0)
    time.sleep(to_sleep)
    end_time = time.time()

    print analyzer.name
    print 'Time = {:.6f}, nodes = {}'.format(end_time - start_time, analysis['stats']['nodes'])
    for line in analysis['result']:
        print '({}) {} ({})'.format(
            line['evaluation'],
            moves_stringify(line['moves'], board.move_up_color),
            moves_stringify(line.get('evaluation_moves', []), board.move_up_color))

    return analysis


def print_simple_eval(board):
    s = time.time()
    simple_eval = simple_evaluation(board, board.move_color)
    e = time.time()
    print
    print 'Time = {:.6f}, nodes = {}'.format(e - s, simple_eval['stats']['nodes'])
    print 'Longest seq = {}'.format(
        moves_stringify(simple_eval['stats']['longest_moves'], board.move_up_color))
    print 'Simple evaluation: {} ({})'.format(
        simple_eval['result']['evaluation'], moves_stringify(simple_eval['result']['moves'], board.move_up_color))


def run_advicer(max_deep, lines, play):
    iteration = 0
    prev_hash = None
    board = None
    while True:
        # Should be in the beginning (continue issue)
        time.sleep(0.005)
        iteration += 1

        s = time.time()
        board = get_board(board)
        # board = get_mock(2)
        e = time.time()

        new_hash = get_pieces_hash(board)
        if prev_hash == new_hash:
            continue
        prev_hash = new_hash

        if board:
            os.system('clear')
            print 'Time: {:.3f}'.format(e - s)
            print 'Iteration: {}'.format(iteration)
            print 'Max deep: {}'.format(max_deep)
            print 'Lines: {}'.format(lines)
            print 'Play: {}'.format(play)
            print

            print_board(board)
            move_up_color = board.move_up_color
            init_move_color = board.init_move_color
            print

            print '{} goes up'.format(move_up_color.upper())
            print '{} to move'.format(init_move_color.upper())
            print 'Evaluation: {}'.format(board.evaluation)
            # print_simple_eval(board)
            # print_take_if_better(board)
            print

            if init_move_color != move_up_color:
                print 'Waiting for opponent move'
                continue

            print 'Calculating lines...'

            result = run_analyzer(board, init_move_color)

            if play:
                moves = result['result'][0]['moves']
                if moves:
                    move = moves[-1]
                    make_move(board, move['position'], move['new_position'])
                else:
                    print 'No moves'
        else:
            print 'No board found'
        print
        print


if __name__ == '__main__':
    max_deep = int(sys.argv[1])
    lines = int(sys.argv[2])
    play = len(sys.argv) > 3 and (sys.argv[3] == '1')

    run_advicer(
        max_deep=max_deep,
        lines=lines,
        play=play
    )
