import time

from analyze import AlphaBetaAnalyzer
from evaluation import take_evaluation
from openings import get_opening_info
from pieces import get_opp_color, BLACK
from utils import moves_stringify, format_move


def run_advicer(mode, max_deep, lines, play, board, board_hashes):
    print 'Run advicer...'

    kwargs = {
        'max_deep': max_deep,
        'lines': lines,
        'evaluation_func': take_evaluation,
        #'max_time': 3
    }
    analyzer = AlphaBetaAnalyzer(**kwargs)
    analysis = run_analyzer(analyzer, board)

    first_line = analysis['result'][0]
    opening_info = get_opening_info(board)
    if opening_info is not None:
        opening_analysis = run_analyzer(analyzer, board, moves_to_consider=[opening_info['move']])
        # TODO: check moves == []
        opening_first_line = opening_analysis['result'][0]
        if (opening_first_line['moves'] and
                abs(first_line['evaluation'] - opening_first_line['evaluation']) < 0.5):
            # If line is exist (moves != []) and evaluation is pretty close to best
            print 'Opening `{}` line selected: {}'.format(
                opening_info['name'], format_move(opening_info['move']))
            first_line = opening_first_line

    # Consider repetition
#     first_line_moves = first_line['moves']
#     if first_line_moves:
#         revert_info = board.make_move(first_line_moves[-1])
#         if board_hashes.get(board.hash) >= 3:
#             analysis = run_analyzer(analyzer, board)
#  
#         board.revert_move(revert_info)

    return first_line


def run_analyzer(analyzer, board, moves_to_consider=None):
    start_time = time.time()
    analysis = analyzer.analyze(board, moves_to_consider=moves_to_consider)
    end_time = time.time() - start_time

    stats = analysis['stats']
    result = analysis['result']
    print
    print 'Analyzer time = {:.6f}, nodes = {}'.format(end_time, stats['nodes'])
    print 'Per node = {:.3f}ms'.format(1000.0 * end_time / stats['nodes'])
    for ind, line in enumerate(result):
        eval_move_color = board.move_color if len(line['moves']) % 2 == 0 else get_opp_color(board.move_color)
        eval_ind = (len(line['moves']) + (1 if board.move_color == BLACK else 0)) / 2 + 1
        print '{}. ({}) {} ({})'.format(
            ind + 1,
            line['evaluation'],
            moves_stringify(line['moves'], board.move_color),
            moves_stringify(line.get('evaluation_moves', []), eval_move_color, ind=eval_ind))

    return analysis
