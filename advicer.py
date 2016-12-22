import random
import time

from analyze import AlphaBetaAnalyzer
from evaluation import take_evaluation
from openings import get_opening_move
from pieces import get_opp_color, BLACK
from utils import moves_stringify, format_move


def run_analyzer(analyzer, board):
    start_time = time.time()
    analysis = analyzer.analyze(board)
    analyzer_time = time.time() - start_time

    print 'Analyzer time = {:.6f}, nodes = {}'.format(analyzer_time, analysis['stats']['nodes'])
    print 'Per node = {:.3f}ms'.format(1000.0 * analyzer_time / analysis['stats']['nodes'])
    for ind, line in enumerate(analysis['result']):
        eval_move_color = board.move_color if len(line['moves']) % 2 == 0 else get_opp_color(board.move_color)
        eval_ind = (len(line['moves']) + (1 if board.move_color == BLACK else 0)) / 2 + 1
        print '{}. ({}) {} ({})'.format(
            ind + 1,
            line['evaluation'],
            moves_stringify(line['moves'], board.move_color),
            moves_stringify(line.get('evaluation_moves', []), eval_move_color, ind=eval_ind))

    return analysis


def run_advicer(mode, max_deep, lines, play, board, prev_analysis):
    print 'Run advicer...'

    kwargs = {
        'max_deep': max_deep,
        'lines': lines,
        'evaluation_func': take_evaluation,
        #'max_time': 1
    }
    analyzer = AlphaBetaAnalyzer(**kwargs)

    start_time = time.time()
    analysis = run_analyzer(analyzer, board)
    opening_move = get_opening_move(board)
    if opening_move is not None:
        opening_analysis = analyzer.analyze(board, moves_to_consider=[opening_move])
        # TODO: check moves == []
        if (opening_analysis['result'][0]['moves'] and
                abs(analysis['result'][0]['evaluation'] - opening_analysis['result'][0]['evaluation']) < 0.5):
            # If line is exist (moves != []) and evaluation is pretty close to best
            analysis = opening_analysis
            print 'Opening move selected'
            print format_move(opening_move)

    spent_time = time.time() - start_time

    if play:
        moves = analysis['result'][0]['moves']
        if moves:
            move = moves[-1]
            if move['captured_piece']:
                # Try to humanize `addy`
                prev_moves = None
                if prev_analysis is not None:
                    prev_moves = prev_analysis['result'][0]['moves']

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
                    move_time = 0.65 + random.random() * 0.2
                    time_to_sleep = max(move_time - spent_time, 0)
                    print 'Sleeping (human unexpected case): {:.3f}'.format(time_to_sleep)
                    time.sleep(time_to_sleep)
        else:
            print 'No moves'

    return analysis
