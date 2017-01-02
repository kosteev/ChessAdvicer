import time

from analyze import AlphaBetaAnalyzer
from evaluation import simple_evaluation
from openings import get_opening_info
from pieces import get_opp_color, BLACK
from utils import moves_stringify, format_move, color_sign


def run_advicer(mode, max_deep, lines, board, board_hashes):
    print 'Run advicer...'
#     a = time.time()
#     pre_analysis = run_analyzer(max_deep, 2, board)
#     for line in pre_analysis['result']:
#         if line['moves']:
#             move = line['moves'][-1]
#             revert_info = board.make_move(move)
#             run_analyzer(
#                 max_deep, lines, board)
#             board.revert_move(revert_info)
#     print '{:.3f}'.format(time.time() - a)
#     a = time.time()
#     pre_analysis = None
#     for move in board.get_board_moves():
#         revert_info = board.make_move(move)
#         if not revert_info:
#             continue
#         print 'Made', format_move(move)
#         pre_analysis = run_analyzer(max_deep - 1, 1, board)
#         board.revert_move(revert_info)
#     if pre_analysis is not None:
#         run_analyzer(max_deep, lines, board, alpha=pre_analysis['result'][0]['evaluation'])
#     print '{:.3f}'.format(time.time() - a)
#     print
#     print

    analysis = run_analyzer(max_deep, lines, board)

    first_line = analysis['result'][0]
    opening_info = get_opening_info(board)
    if opening_info is not None:
        opening_analysis = run_analyzer(
            max_deep, 1, board, moves_to_consider=[opening_info['move']])
        # TODO: check moves == []
        opening_first_line = opening_analysis['result'][0]
        if (opening_first_line['moves'] and
                abs(first_line['evaluation'] - opening_first_line['evaluation']) < 0.5):
            # If line is exist (moves != []) and evaluation is pretty close to best
            print 'Opening `{}` line selected: {}'.format(
                opening_info['name'], format_move(opening_info['move']))
            first_line = opening_first_line

    # Consider repetition
    first_line_moves = first_line['moves']
    sign = color_sign(board.move_color)
    if first_line_moves:
        revert_info = board.make_move(first_line_moves[-1])
        if board_hashes.get(board.hash) >= 1:
            board.revert_move(revert_info)

            print
            print 'First line leads to two times repetition'
            proper_evaluation = -2.5
            if sign * first_line['evaluation'] > proper_evaluation:
                # If position is not so bad, prevent three times repetition
                # Try to find another line
                analysis = run_analyzer(max_deep, 2, board)
                result = analysis['result']
                if (first_line_moves[-1] != result[0]['moves'][-1] and
                        sign * result[0]['evaluation'] > proper_evaluation):
                    first_line = result[0]
                elif (len(result) > 1 and
                        sign * result[1]['evaluation'] > proper_evaluation):
                    first_line = result[1]
                else:
                    print 'Not found any other good line'

                print 'Selected line: ({}) {}'.format(
                    first_line['evaluation'], moves_stringify(board, first_line['moves']))
            else:
                print 'Position is not so good to prevent repetitions'
        else:
            board.revert_move(revert_info)

    return first_line


def run_analyzer(max_deep, lines, board, moves_to_consider=None):
    kwargs = {
        'max_deep': max_deep,
        'max_deep_captures': 2,
        'max_deep_one_capture': 999,
        'lines': lines,
        'evaluation_func': simple_evaluation,
    }

    start_time = time.time()
    analyzer = AlphaBetaAnalyzer(**kwargs)
    analysis = analyzer.analyze(board, moves_to_consider=moves_to_consider)
    end_time = time.time() - start_time

    stats = analysis['stats']
    result = analysis['result']
    print
    print 'Analyzer time = {:.6f}, nodes = {}'.format(end_time, stats['nodes'])
    # print 'Per node = {:.3f}ms'.format(1000.0 * end_time / stats['nodes'])
    for ind, line in enumerate(result):
        print '{}. ({}) {}'.format(
            ind + 1,
            line['evaluation'],
            moves_stringify(board, line['moves']))

    return analysis
