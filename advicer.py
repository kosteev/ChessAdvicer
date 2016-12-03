import os
import sys
import time

from analyze import SimpleAnalyzer, AlphaAnalyzer, AlphaBetaAnalyzer
from board_detection import get_board
from evaluation import simple_evaluation
from gui import make_move
from mocks import get_mock
from utils import get_pieces_hash, format_move, print_board


# 2minutes - deep=3
# 3minutes - deep=4


def moves_stringify(moves, move_up_color):
    return '; '.join(
        [format_move(move, move_up_color)
         for move in reversed(moves)])


def run_analyzer(analyzer, board, move_color):
    data = {
        'nodes': 0
    }
    # TODO: (kosteev) write in the process of dfs working
    start_time = time.time()
    result = analyzer.dfs(
        board, move_color, data=data)
    end_time = time.time()

    print analyzer.name
    print 'Time = {:.3f}, nodes = {}'.format(end_time - start_time, data['nodes'])
    for ind, line in enumerate(result):
        print '{}. ({}) {}'.format(
            ind + 1, line['evaluation'],
            moves_stringify(line['moves'], board.move_up_color))

    return result


def print_simple_eval(board):
    data = {
        'nodes': 0,
        'longest_moves': []
    }
    s = time.time()
    simple_eval = simple_evaluation(board, board.move_color, data)
    e = time.time()
    print
    print 'Time = {:.3f}, nodes = {}'.format(e - s, data['nodes'])
    print 'Longest seq = {}'.format(
        moves_stringify(data['longest_moves'], board.move_up_color))
    print 'Simple evaluation: {} ({})'.format(
        simple_eval['evaluation'], moves_stringify(simple_eval['moves'], board.move_up_color))


def run_advicer():
    max_deep = int(sys.argv[1])
    lines = int(sys.argv[2])
    play = len(sys.argv) > 3 and (sys.argv[3] == '1')
    simple_analyzer = SimpleAnalyzer(max_deep=max_deep, lines=lines)
    alpha_analyzer = AlphaAnalyzer(max_deep=max_deep, lines=lines)
    alpha_beta_analyzer = AlphaBetaAnalyzer(max_deep=max_deep, lines=lines)
    alpha_beta_analyzer_evaluation = AlphaBetaAnalyzer(
        max_deep=10, lines=10)

    iteration = 0
    prev_hash = None
    while True:
        # Should be in the beginning (continue issue)
        time.sleep(0.005)
        iteration += 1

        s = time.time()
        board = get_board()
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
            move_color = board.move_color
            init_eval = board.get_pieces_eval()
            print

            print '{} goes up'.format(move_up_color.upper())
            print '{} to move'.format(move_color.upper())
            print 'Evaluation: {}'.format(init_eval)
            # print_simple_eval(board)
            print

            if move_color != move_up_color:
                print 'Waiting for opponent move'
                continue

            print 'Calculating lines...'

            # run_analyzer(simple_analyzer, board, move_color)
            # run_analyzer(alpha_analyzer, board, move_color)
            result = run_analyzer(alpha_beta_analyzer, board, move_color)
            # run_analyzer(alpha_beta_analyzer_evaluation, board, move_color)

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


if __name__ == '__main__':
    run_advicer()
