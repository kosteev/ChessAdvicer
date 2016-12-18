import os
import psutil
import random
import sys
import time

from analyze import SimpleAnalyzer, AlphaAnalyzer, AlphaBetaAnalyzer
from board_detection import get_board
from evaluation import simple_evaluation, take_evaluation
from gui import make_move
from mocks import get_mock
from pieces import get_opp_color, BLACK
from utils import print_board, moves_stringify


def run_analyzer(analyzer_class, board, max_deep, lines, play):
    kwargs = {
        'max_deep': max_deep,
        'lines': lines,
        'evaluation_func': take_evaluation,
        #'max_time': 1,
    }
    analyzer = analyzer_class(**kwargs)

    start_time = time.time()
    analysis = analyzer.analyze(board)
    analyzer_time = time.time() - start_time
    print 'Analyzer time = {:.6f}, nodes = {}'.format(analyzer_time, analysis['stats']['nodes'])
    print 'Per node = {:.3f}ms'.format(1000.0 * analyzer_time / analysis['stats']['nodes'])
    for line in analysis['result']:
        eval_move_color = board.move_color if len(line['moves']) % 2 == 0 else get_opp_color(board.move_color)
        eval_ind = (len(line['moves']) + (1 if board.move_color == BLACK else 0)) / 2 + 1
        print '({}) {} ({})'.format(
            line['evaluation'],
            moves_stringify(line['moves'], board.move_color),
            moves_stringify(line.get('evaluation_moves', []), eval_move_color, ind=eval_ind))
    print

    analyze_moves_order = {}
    for deep in xrange(max_deep - 1, max_deep + 1):
        kwargs = {
            'max_deep': deep,
            'lines': lines if deep == max_deep else 3,
            'evaluation_func': take_evaluation,
            #'max_time': 1,
            'analyze_moves_order': analyze_moves_order
        }
        analyzer = analyzer_class(**kwargs)
    
        start_time = time.time()
        analysis = analyzer.analyze(board)
        analyzer_time = time.time() - start_time
        print 'Analyzer time = {:.6f}, nodes = {}'.format(analyzer_time, analysis['stats']['nodes'])
        print 'Per node = {:.3f}ms'.format(1000.0 * analyzer_time / analysis['stats']['nodes'])
        for line in analysis['result']:
            eval_move_color = board.move_color if len(line['moves']) % 2 == 0 else get_opp_color(board.move_color)
            eval_ind = (len(line['moves']) + (1 if board.move_color == BLACK else 0)) / 2 + 1
            print '({}) {} ({})'.format(
                line['evaluation'],
                moves_stringify(line['moves'], board.move_color),
                moves_stringify(line.get('evaluation_moves', []), eval_move_color, ind=eval_ind))
        print

        analyze_moves_order = {
            0: [(line['moves'][-1]['position'], line['moves'][-1]['new_position'])
                for line in analysis['result']]
        }

    return analysis


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


def run_advicer(mode, max_deep, lines, play):
    iteration = 0
    prev_hash = None
    board = None
    while True:
        # Should be in the beginning (continue issue)
        time.sleep(0.005)
        iteration += 1

        s = time.time()
        board = get_board(mode, board)
        # board = get_mock(2)
        e = time.time()

        new_hash = -1337
        if board:
            new_hash = board.hash
        if prev_hash == new_hash:
            continue
        prev_hash = new_hash

        if board:
            os.system('clear') 
            print 'Memory usage: {} M'.format(
                psutil.Process(os.getpid()).memory_info().rss / 1000 / 1000)
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

            print 'Calculating lines...'

            # result = run_analyzer(SimpleAnalyzer, board, max_deep, lines, play)
            # result = run_analyzer(AlphaAnalyzer, board, max_deep, lines, play)
            result = run_analyzer(AlphaBetaAnalyzer, board, max_deep, lines, play)

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
    mode = sys.argv[1]
    max_deep = int(sys.argv[2])
    lines = int(sys.argv[3])
    play = len(sys.argv) > 4 and (sys.argv[4] == '1')

    run_advicer(
        mode=mode,
        max_deep=max_deep,
        lines=lines,
        play=play
    )
