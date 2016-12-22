import random
import time

from analyze import AlphaBetaAnalyzer
from evaluation import take_evaluation
from pieces import get_opp_color, BLACK
from utils import moves_stringify


def run_analyzer(analyzer_class, board, max_deep, lines, play):
    kwargs = {
        'max_deep': max_deep,
        'lines': lines,
        'evaluation_func': take_evaluation,
        #'max_time': 1
    }
    analyzer = analyzer_class(**kwargs)

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


def run_advicer(mode, max_deep, lines, play, board, prev_result):
    print 'Calculating lines...'
    start_time = time.time()
    result = run_analyzer(AlphaBetaAnalyzer, board, max_deep, lines, play)
    analyzer_time = time.time() - start_time

    if play:
        moves = result['result'][0]['moves']
        if moves:
            move = moves[-1]
            if move['captured_piece']:
                # Try to humanize `addy`
                prev_moves = None
                if prev_result is not None:
                    prev_moves = prev_result['result'][0]['moves']

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
                    time_to_sleep = max(move_time - analyzer_time, 0)
                    print 'Sleeping (human unexpected case): {:.3f}'.format(time_to_sleep)
                    time.sleep(time_to_sleep)

    return result
