from board import Board
from pieces import get_opp_color, WHITE
from utils import color_sign


def simple_evaluation(board, move_color, data):
    '''
    Evaluates position.

    Makes a move with the most valuable take.
    Takes best of this or current material evaluation.
    # TODO: (kosteev) consider other cases if take is worse than current material evaluation.
    '''
    data['nodes'] += 1

    opp_move_color = get_opp_color(move_color)
    sign = color_sign(move_color)
    is_any_move = False
    gen = board.generate_next_board(move_color, sort_key=Board.SORT_BY_TAKE_VALUE)

    evaluation = board.get_pieces_eval()
    evaluation_moves = []
    for move in gen:
        is_any_move = True
        if not move['new_position_old_piece']:
            # Consider only takes
            break

        data['longest_moves'] = [move] + data['longest_moves']
        cand = simple_evaluation(
            board, opp_move_color, data)

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
        if board.is_check(opp_move_color):
            # Checkmate
            # ???? self.MAX_EVALUATION / 2
            return {
                'evaluation': -sign * Board.MAX_EVALUATION / 2,
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
