from board import Board
from pieces import WHITE, PIECES
from utils import color_sign


def material_evaluation(board):
    stats = {}
    result = {
        'evaluation': board.material,
        'moves': []
    }

    return {
        'result': result,
        'stats': stats
    }


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


def take_evaluation_dfs(board, stats, max_piece_value=PIECES['queen']['value']):
    '''
    Evaluates position.

    Makes a move with the most valuable take.
    Takes best of this or current material evaluation.

    # TODO: (kosteev) consider other cases if take is worse than current material evaluation.
    # TODO: (kosteev) make it faster, cut with alpha/beta algo.


    Disadvantages:
    1. If two takes are available considers not the best
    2.
    '''
    stats['nodes'] += 1

    move_color = board.move_color
    sign = color_sign(move_color)
    is_any_move = False

    evaluation = board.evaluation
    evaluation_moves = []
    for move in board.get_board_moves(capture_sort_key=Board.sort_take_by_value):
        revert_info = board.make_move(move)
        if revert_info is None:
            continue

        is_any_move = True
        if not move['captured_piece']:
            # Consider only takes
            board.revert_move(revert_info)
            break
        captured_piece_value = PIECES[move['captured_piece']]['value']
        if captured_piece_value > max_piece_value:
            board.revert_move(revert_info)

            # Break recursion, do not consider line if opponent takes more valuable piece
            # Return something that will not affect result
            evaluation = sign * (Board.MAX_EVALUATION + 1)
            evaluation_moves = []
            break

        stats['longest_moves'] = [move] + stats['longest_moves']
        cand = take_evaluation_dfs(
            board, stats, captured_piece_value)
        board.revert_move(revert_info)

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
