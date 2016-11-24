from pieces import MOVE_UP_COLOR
from utils import get_opp_color, get_pieces_eval, get_piece_moves, cell_name


# 1. Kings can be taken both
# 2. No pieces on board of one color
# 3. 



# - implement true check and mate
# - evaluation with brute force with good takes

MAX_EVALUATION = 1000
MAX_DEEP = 4


def on_board((c, r)):
    return 0 <= c < 8 and 0 <= r < 8 


def dfs(pieces, move_color, data, alpha=None, deep=0):
    '''
    Not less than 
    '''
    if alpha is None:
        alpha = -MAX_EVALUATION

    data['nodes'] += 1

    if deep == MAX_DEEP:
        return [], get_pieces_eval(pieces)

    opp_move_color = get_opp_color(move_color)
    sign = 1 if move_color == MOVE_UP_COLOR else -1

    evaluation_plus = None
    best_moves = []
    gen = generate_next_pieces(pieces, move_color)
    for move in gen:
        best_moves_cand, evaluation_cand = dfs(
            pieces, opp_move_color, data, alpha=evaluation_plus, deep=deep + 1)
        evaluation_cand_plus = sign * evaluation_cand

        if not evaluation_plus or evaluation_plus < evaluation_cand_plus:
            evaluation_plus = evaluation_cand_plus
            best_moves = [move] + best_moves_cand

        if evaluation_plus >= -1 * alpha:
            try:
                gen.send(True)
            except StopIteration:
                pass
            break

    if evaluation_plus is None:
        if is_check(pieces, opp_move_color):
            # Checkmate
            evaluation_plus = -(MAX_EVALUATION - deep)
        else:
            # Draw
            evaluation_plus = 0

    return best_moves, sign * evaluation_plus


def is_check(pieces, move_color):
    '''
    Determines if check is by move_color to opposite color
    '''
    check = False
    for _ in generate_next_pieces(pieces, move_color, check=True):
        check = True
        # Allow to end this loop to release generator

    return check


def generate_next_pieces(
        pieces, move_color, check=False):
    '''
    pieces = {(1, 2): ('rook', 'white)}
    '''
    opp_move_color = get_opp_color(move_color)

    for position, (piece, color) in pieces.items():
        if color != move_color:
            continue

        for variant in get_piece_moves(pieces, position):
            for diff in variant:
                new_position = (position[0] + diff[0], position[1] + diff[1])

                if not on_board(new_position):
                    break

                new_position_piece = pieces.get(new_position)
                last_diff = False
                if new_position_piece:
                    if new_position_piece[1] == move_color:
                        break
                    else:
                        last_diff = True

                if check:
                    if new_position_piece == ('king', opp_move_color):
                        yield position, new_position
                        return
                else:
                    # Make move
                    pieces[new_position] = pieces[position]
                    del pieces[position]
                    if (pieces[new_position][0] == 'pawn' and
                            new_position[1] in [0, 7]):
                        # Promote to queen
                        # TODO: (kosteev) consider other promotions
                        pieces[new_position] = ('queen', pieces[new_position][1])
    
                    finish = False
                    if not is_check(pieces, opp_move_color):
                        finish = yield position, new_position
    
                    # Recover
                    pieces[position] = (piece, color)
                    if new_position_piece:
                        pieces[new_position] = new_position_piece
                    else:
                        del pieces[new_position]

                    if finish:
                        return

                if last_diff:
                    break
