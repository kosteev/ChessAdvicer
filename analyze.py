from pieces import WHITE, BLACK, PIECES
from utils import get_opp_color, get_pieces_eval, get_piece_moves, color_sign


# - implement true check and mate
# - evaluation with brute force with good takes
# - auto up color

MAX_EVALUATION = 1000


class Analyzer(object):
    def __init__(self, max_deep, lines=1):
        self.max_deep = max_deep
        self.lines = lines

    @staticmethod
    def on_board((c, r)):
        return 0 <= c < 8 and 0 <= r < 8

    def dfs(self, board, move_color, data, alpha=None, deep=0):
        '''
        alpha - to reduce brute force
            if alpha is None dfs will return always eval not None
        max_deep - 2*n for checkmate in `n` moves

        TODO: (kosteev) write tests
        '''
        data['nodes'] += 1
        if deep == self.max_deep:
            return get_pieces_eval(board), []

        opp_move_color = get_opp_color(move_color)

        gen = self.generate_next_pieces(board, move_color)
        best_evaluation = None
        best_moves = None
        for move in gen:
            cand = self.dfs(
                board, opp_move_color, data,
                alpha=best_evaluation, deep=deep + 1)
            if cand is None:
                # Not found better move
                continue
            cand_evaluation, cand_moves = cand

            if move_color == WHITE:
                if (best_evaluation is None or
                        best_evaluation < cand_evaluation):
                    best_evaluation = cand_evaluation
                    best_moves = cand_moves + [move]
            else:
                if (best_evaluation is None or
                        best_evaluation > cand_evaluation):
                    best_evaluation = cand_evaluation
                    best_moves = cand_moves + [move]

            # TODO: (kosteev) cut two deep recursion
            if alpha is not None:
                if (move_color == BLACK and best_evaluation <= alpha or
                        move_color == WHITE and best_evaluation >= alpha):
                    try:
                        gen.send(True)
                    except StopIteration:
                        pass
                    return None

        sign = color_sign(move_color)
        if best_evaluation is None:
            if self.is_check(board, opp_move_color):
                # Checkmate
                best_evaluation = -sign * (MAX_EVALUATION - deep)
                best_moves = []
            else:
                # Draw
                best_evaluation = 0
                best_moves = []

        return best_evaluation, best_moves

    @staticmethod
    def is_check(board, move_color):
        '''
        Determines if check is by move_color to opposite color
        '''
        check = False
        for _ in Analyzer.generate_next_pieces(board, move_color, check=True):
            check = True
            # Allow to end this loop to release generator

        return check

    @staticmethod
    def generate_next_pieces(
            board, move_color, check=False):
        '''
        pieces = {(1, 2): ('rook', 'white)}
        '''
        opp_move_color = get_opp_color(move_color)
        pieces = board['pieces']

        pieces_list = []
        for position, (piece, color) in pieces.items():
            if color != move_color:
                continue
            pieces_list.append((position, (piece, color)))
        pieces_list.sort(key=lambda x: PIECES[x[1][0]]['priority'], reverse=True)

        for position, (piece, color) in pieces_list:
            for variant in get_piece_moves(board, position):
                for diff in variant:
                    new_position = (position[0] + diff[0], position[1] + diff[1])

                    if not Analyzer.on_board(new_position):
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
                            yield
                            return
                    else:
                        # Make move (consider, promotions)
                        pieces[new_position] = (diff[2] or pieces[position][0], pieces[position][1])
                        del pieces[position]

                        finish = False
                        if not Analyzer.is_check(board, opp_move_color):
                            finish = yield {
                                'position': position,
                                'new_position': new_position,
                                'piece': piece,
                                'new_piece': pieces[new_position][0],
                                'is_take': True if new_position_piece else False
                            }

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
