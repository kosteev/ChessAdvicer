import time

from analyze import AlphaBetaAnalyzer
from evaluation import take_evaluation
from openings import get_opening_info
from pieces import get_opp_color, BLACK, WHITE
from utils import moves_stringify, format_move


def run_advicer(mode, max_deep, lines, play, board):
    print 'Run advicer...'

    kwargs = {
        'max_deep': max_deep,
        'lines': lines,
        'evaluation_func': take_evaluation,
        #'max_time': 1
    }
    analyzer = AlphaBetaAnalyzer(**kwargs)

    start_time = time.time()
    analysis = analyzer.analyze(board)

    # Get more deep analysis
#     deep_kwargs = {
#         'max_deep': max_deep,
#         'lines': 1,
#         'evaluation_func': take_evaluation,
#         #'max_time': 1
#     }
#     deep_analyzer = AlphaBetaAnalyzer(**deep_kwargs)
#     moves_to_consider = []
#     for line in analysis['result']:
#         if line['moves']:
#             moves_to_consider.append(line['moves'][-1])
# 
#     alpha = None
#     beta = None
#     for move in moves_to_consider:
#         revert_info = board.make_move(move)
#         analyze_kwargs = {}
#         if alpha is not None:
#             analyze_kwargs['alpha'] = alpha
#         if beta is not None:
#             analyze_kwargs['beta'] = beta
#         deeper_analysis = deep_analyzer.analyze(board, **analyze_kwargs)
#         line = deeper_analysis['result'][0]
#         print line['evaluation'], format_move(move), moves_stringify(line['moves'], board.move_color)
#         board.revert_move(revert_info)
#         if board.move_color == WHITE:
#             if alpha is None:
#                 alpha = line['evaluation']
#             else:
#                 alpha = max(alpha, line['evaluation'])
#         else:
#             if beta is None:
#                 beta = line['evaluation']
#             else:
#                 beta = min(beta, line['evaluation'])

    first_line = analysis['result'][0]
    opening_info = get_opening_info(board)
    if opening_info is not None:
        opening_analysis = analyzer.analyze(board, moves_to_consider=[opening_info['move']])
        # TODO: check moves == []
        if (opening_analysis['result'][0]['moves'] and
                abs(analysis['result'][0]['evaluation'] - opening_analysis['result'][0]['evaluation']) < 0.5):
            # If line is exist (moves != []) and evaluation is pretty close to best
            print 'Opening `{}` line selected: {}'.format(
                opening_info['name'], format_move(opening_info['move']))
            first_line = opening_analysis['result'][0]
    advicer_time = time.time() - start_time

    print 'Advicer time = {:.6f}, nodes = {}'.format(advicer_time, analysis['stats']['nodes'])
    print 'Per node = {:.3f}ms'.format(1000.0 * advicer_time / analysis['stats']['nodes'])
    for ind, line in enumerate(analysis['result']):
        eval_move_color = board.move_color if len(line['moves']) % 2 == 0 else get_opp_color(board.move_color)
        eval_ind = (len(line['moves']) + (1 if board.move_color == BLACK else 0)) / 2 + 1
        print '{}. ({}) {} ({})'.format(
            ind + 1,
            line['evaluation'],
            moves_stringify(line['moves'], board.move_color),
            moves_stringify(line.get('evaluation_moves', []), eval_move_color, ind=eval_ind))

    return first_line
