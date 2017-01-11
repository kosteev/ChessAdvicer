import time

from analyze import AlphaBetaAnalyzer
from evaluation import simple_evaluation
from openings import get_opening_info
from utils import moves_stringify, format_move, color_sign


def run_advicer(mode, max_deep, lines, board, board_hashes):
    print 'Run advicer...'
    max_deep_captures = 1

#     a = time.time()
#     pre_analysis = run_analyzer(
#         max_deep=1, max_deep_captures=1, lines=999, board=board)
#     pre_moves = [
#         line['moves'][-1]
#         for line in pre_analysis['result']
#         if line['moves']
#     ]
#     print '{:.3f}'.format(time.time() - a)
# 
#     pre_analysis = run_analyzer(
#         max_deep=max_deep, max_deep_captures=max_deep_captures, lines=lines,
#         board=board, moves_to_consider=pre_moves)
#     print '{:.3f}'.format(time.time() - a)
#     print
#     print

    analysis = run_analyzer(
        max_deep=max_deep, max_deep_captures=max_deep_captures, lines=lines, board=board)

    first_line = analysis['result'][0]
    opening_info = get_opening_info(board)
    if opening_info is not None:
        opening_analysis = run_analyzer(
            max_deep=max_deep, max_deep_captures=max_deep_captures,
            lines=1, board=board, moves_to_consider=[opening_info['move']])
        # TODO: check moves == []
        opening_first_line = opening_analysis['result'][0]
        if (opening_first_line['moves'] and
                abs(first_line['evaluation'] - opening_first_line['evaluation']) < 0.5):
            # If line is exist (moves != []) and evaluation is pretty close to best
            print 'Opening `{}` line selected: {}'.format(
                opening_info['name'], format_move(board, opening_info['move']))
            first_line = opening_first_line

    # Consider repetition
    first_line_moves = first_line['moves']
    sign = color_sign(board.move_color)
    if first_line_moves:
        revert_info = board.make_move(first_line_moves[-1])
        board_hash = board.hash
        board.revert_move(revert_info)

        if board_hashes.get(board_hash, 0) >= 1:
            print
            print 'First line leads to two times repetition'
            proper_evaluation = -2.5
            if sign * first_line['evaluation'] > proper_evaluation:
                # If position is not so bad, prevent three times repetition
                # Try to find another line
                analysis = run_analyzer(
                    max_deep=max_deep, max_deep_captures=max_deep_captures, lines=3, board=board)
                result = analysis['result']

                candidates = []
                for line in result:
                    # It will always has moves, because at least one line has moves (first_line)
                    revert_info = board.make_move(line['moves'][-1])
                    board_hash = board.hash
                    board.revert_move(revert_info)

                    # Collect all appropriate lines
                    if (sign * line['evaluation'] > proper_evaluation and
                            board_hashes.get(board_hash, 0) <= 1):
                        candidates.append((board_hashes.get(board_hash, 0), line))

                # Use stability of sort
                # Select the rarest proper line (with better evaluation)
                candidates.sort(key=lambda x: x[0])
                if candidates:
                    first_line = candidates[0][1]
                else:
                    print 'Not found any other good line'

                print 'Selected line: ({}) {}'.format(
                    first_line['evaluation'], moves_stringify(board, first_line['moves']))
            else:
                print 'Position is not so good to prevent repetitions'

    return first_line


def run_analyzer(max_deep, max_deep_captures, lines, board, moves_to_consider=None):
    kwargs = {
        'max_deep': max_deep,
        'max_deep_captures': max_deep_captures,
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
