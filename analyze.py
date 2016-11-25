from pieces import MOVE_UP_COLOR
from utils import get_opp_color, get_pieces_eval, get_piece_moves


# - implement true check and mate
# - evaluation with brute force with good takes
# - second and third line
# - auto up color

MAX_EVALUATION = 1000
MAX_DEEP = 4  # 2*n for checkmate in `n` moves


def on_board((c, r)):
    return 0 <= c < 8 and 0 <= r < 8 


def dfs(pieces, move_color, data, alpha=None, deep=0, lines=1):
    if alpha is None:
        alpha = -MAX_EVALUATION

    data['nodes'] += 1

    if deep == MAX_DEEP:
        return [[get_pieces_eval(pieces, move_color), []]]

    opp_move_color = get_opp_color(move_color)

    result = [] # Sorted by desc, (eval, moves). Related to move color
    gen = generate_next_pieces(pieces, move_color)
    for move in gen:
        results_cand = dfs(
            pieces, opp_move_color, data, alpha=result[-1][0] if result else None, deep=deep + 1)
        result_cand = results_cand[0]
        result_cand[0] *= -1
        result_cand[1].append(move)
        result.append(result_cand)

        result.sort(key=lambda (e, ms): e, reverse=True)
        result = result[:lines]

        if result[0][0] >= -1 * alpha:
            try:
                gen.send(True)
            except StopIteration:
                pass
            break

    if not result:
        if is_check(pieces, opp_move_color):
            # Checkmate
            result = [[-(MAX_EVALUATION - deep), []]]
        else:
            # Draw
            result = [[0, []]]

    return result


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
                        # Promote to new piece
                        print diff
                        pieces[new_position] = (diff[2], pieces[new_position][1])
    
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
