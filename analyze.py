from pieces import WHITE, BLACK, get_opp_color
from utils import get_pieces_eval, color_sign, print_board


# - implement true check and mate
# - evaluation with brute force with good takes


class Analyzer(object):
    MAX_EVALUATION = 1000

    def __init__(self, max_deep, lines=1):
        self.max_deep = max_deep
        self.lines = lines


class AlphaAnalyzer(Analyzer):
    def dfs(self, board, move_color, data, alpha=None, deep=0):
        '''
        alpha - to reduce brute force
            if alpha is None dfs will return always list not 0-length
        max_deep - 2*n for checkmate in `n` moves

        TODO: (kosteev) write tests
        '''
        data['nodes'] += 1
        if deep == self.max_deep:
            return [{
                'evaluation': get_pieces_eval(board),
                'moves': []
            }]

        opp_move_color = get_opp_color(move_color)

        gen = board.generate_next_board(move_color)
        result = []
        lines = self.lines if deep == 0 else 1
        for move in gen:
            cand = self.dfs(
                board, opp_move_color, data,
                alpha=result[-1]['evaluation'] if len(result) == lines else None, deep=deep + 1)
            if cand is None:
                # Not found better move
                continue

            result.append(cand[0])
            result[-1]['moves'].append(move)
            result.sort(
                key=lambda x: x['evaluation'], reverse=(move_color==WHITE))
            result = result[:lines]

            # TODO: (kosteev) cut two deep recursion
            if alpha is not None:
                if (move_color == BLACK and result[0]['evaluation'] <= alpha or
                        move_color == WHITE and result[0]['evaluation'] >= alpha):
                    try:
                        gen.send(True)
                    except StopIteration:
                        pass
                    return None

        sign = color_sign(move_color)
        if not result:
            if board.is_check(opp_move_color):
                # Checkmate
                result = [{
                    'evaluation': -sign * (self.MAX_EVALUATION - deep),
                    'moves': []
                }]
            else:
                # Draw
                result = [{
                    'evaluation': 0,
                    'moves': []
                }]

        return result


class AlphaBetaAnalyzer(Analyzer):
    def dfs(self, board, move_color, data,
            alpha=-Analyzer.MAX_EVALUATION - 1, beta=Analyzer.MAX_EVALUATION + 1, deep=0):
        '''
        alpha - to reduce brute force
            if alpha and beta not passed dfs will return always list not 0-length
        max_deep - 2*n for checkmate in `n` moves

        TODO: (kosteev) write tests
        '''
        data['nodes'] += 1
        if deep == self.max_deep:
            return [{
                'evaluation': get_pieces_eval(board),
                'moves': []
            }]

        opp_move_color = get_opp_color(move_color)

        lines = self.lines if deep == 0 else 1
        result = []
        is_any_move = False
        gen = board.generate_next_board(move_color)
        for move in gen:
            is_any_move = True

            # !!!!! Here is bug related to lines
            cand = self.dfs(
                board, opp_move_color, data,
                alpha=alpha, beta=beta, deep=deep + 1)
            if not cand:
                # Not found better move
                continue

            result.append(cand[0])
            result[-1]['moves'].append(move)
            result.sort(
                key=lambda x: x['evaluation'], reverse=(move_color==WHITE))
            result = result[:lines]

            # !!!!! Here is bug related to lines
            if move_color == WHITE:
                alpha = max(alpha, result[0]['evaluation'])
            else:
                beta = min(beta, result[0]['evaluation'])

            # >= ? >
            # Try both and see how many nodes
            if alpha >= beta:
                try:
                    gen.send(True)
                except StopIteration:
                    pass
                return []

        sign = color_sign(move_color)
        if not is_any_move:
            if board.is_check(opp_move_color):
                # Checkmate
                result = [{
                    'evaluation': -sign * (self.MAX_EVALUATION - deep),
                    'moves': []
                }]
            else:
                # Draw
                result = [{
                    'evaluation': 0,
                    'moves': []
                }]

        return result
