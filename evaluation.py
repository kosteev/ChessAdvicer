from board import Board
from pieces import WHITE
from utils import color_sign


def simple_evaluation(board):
    stats = {}
    result = {
        'evaluation': board.evaluation,
        'moves': []
    }

    return {
        'result': result,
        'stats': stats
    }


def take_evaluation(board):
    stats = {
        'nodes': 0,
        'longest_moves': []
    }
    result = take_evaluation_dfs(board, stats)
    return {
        'result': result,
        'stats': stats
    }


def take_evaluation_dfs(board, stats):
    '''
    Evaluates position.

    Makes a move with the most valuable take.
    Takes best of this or current material evaluation.
    # TODO: (kosteev) consider other cases if take is worse than current material evaluation.
    # TODO: (kosteev) make it faster, cut with alpha/beta algo.
    '''
    stats['nodes'] += 1

    move_color = board.move_color
    sign = color_sign(move_color)
    is_any_move = False

    gen = board.generate_next_board(capture_sort_key=Board.sort_take_by_value)

    evaluation = board.evaluation + board.probable_moves_count / 1000.0
    evaluation_moves = []
    for move in gen:
        is_any_move = True
        if not move['captured_piece']:
            # Consider only takes
            break

        stats['longest_moves'] = [move] + stats['longest_moves']
        cand = take_evaluation_dfs(
            board, stats)

        # TODO: (kosteev) consider no moves
        if move_color == WHITE:
            if cand['evaluation'] > evaluation:
                evaluation = cand['evaluation']
                evaluation_moves = cand['moves'] + [move]
        else:
            if cand['evaluation'] < evaluation:
                evaluation = cand['evaluation']
                evaluation_moves = cand['moves'] + [move]
        break
    try:
        gen.send(True)
    except StopIteration:
        pass

    if not is_any_move:
        if board.is_check(opposite=True):
            # Checkmate
            # ???? self.MAX_EVALUATION / 2
            return {
                'evaluation': -sign * Board.MAX_EVALUATION / 5,
                'moves': []
            }
        else:
            # Draw
            return {
                'evaluation': 0,
                'moves': []
            }

    return {
        'evaluation': evaluation,
        'moves': evaluation_moves
    }
