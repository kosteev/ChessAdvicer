import os
import sys
import time

from analyze import AlphaBetaAnalyzer
from board_detection import get_board
from evaluation import simple_evaluation, take_if_better
from gui import make_move
from utils import get_pieces_hash, format_move, print_board


def moves_stringify(moves, move_up_color):
    return '; '.join(
        [format_move(move, move_up_color)
         for move in reversed(moves)])


def run_analyzer(analyzer, board):
    # TODO: (kosteev) write in the process of dfs working
    start_time = time.time()
    result = analyzer.guess_move(board)
    end_time = time.time()

    print analyzer.name
    print 'Time = {:.6f}, nodes = {}'.format(end_time - start_time, result['data']['nodes'])
    for ind, line in enumerate(result['result']):
        print '{}. ({}) {}'.format(
            ind + 1, line['evaluation'],
            moves_stringify(line['moves'], board.move_up_color))
        print moves_stringify(line.get('eval_data', {}).get('longest_moves', []), board.move_up_color)

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
    print 'Time = {:.6f}, nodes = {}'.format(e - s, data['nodes'])
    print 'Longest seq = {}'.format(
        moves_stringify(data['longest_moves'], board.move_up_color))
    print 'Simple evaluation: {} ({})'.format(
        simple_eval['evaluation'], moves_stringify(simple_eval['moves'], board.move_up_color))


def print_take_if_better(board):
    data = {
        'nodes': 0,
        'longest_moves': []
    }
    s = time.time()
    take_if_better_eval = take_if_better(board, board.move_color, data)
    e = time.time()
    print
    print 'Time = {:.3f}, nodes = {}'.format(e - s, data['nodes'])
    print 'Longest seq = {}'.format(
        moves_stringify(data['longest_moves'], board.move_up_color))
    print 'Take if better evaluation: {} ({})'.format(
        take_if_better_eval['evaluation'], moves_stringify(take_if_better_eval['moves'], board.move_up_color))


def run_advicer():
    max_deep = int(sys.argv[1])
    lines = int(sys.argv[2])
    play = len(sys.argv) > 3 and (sys.argv[3] == '1')
    alpha_beta_analyzer = AlphaBetaAnalyzer(max_deep=max_deep, lines=lines)

    iteration = 0
    prev_hash = None
    board = None
    while True:
        # Should be in the beginning (continue issue)
        time.sleep(0.010)
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
            move_color = board.move_color
            print

            print '{} goes up'.format(move_up_color.upper())
            print '{} to move'.format(move_color.upper())
            print 'Evaluation: {}'.format(board.evaluation)
            # print_simple_eval(board)
            # print_take_if_better(board)
            print

            if move_color != move_up_color:
                print 'Waiting for opponent move'
                continue

            print 'Calculating lines...'

            result = run_analyzer(alpha_beta_analyzer, board)

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
