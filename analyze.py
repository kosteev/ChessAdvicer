from pieces import WHITE, BLACK, get_opp_color
from utils import color_sign


# - implement true check and mate
# - evaluation with brute force with good takes


class Analyzer(object):
    MAX_EVALUATION = 1000

    def __init__(self, max_deep, lines=1, evaluation=False):
        self.max_deep = max_deep
        self.lines = lines
        self.evaluation = evaluation


class SimpleAnalyzer(Analyzer):
    name = 'SimpleAnalyzer'

    def dfs(self, board, move_color, data, deep=0):
        '''
        max_deep - 2*n for checkmate in `n` moves

        TODO: (kosteev) write tests
        '''
        data['nodes'] += 1
        if deep == self.max_deep:
            return [{
                'evaluation': board.get_pieces_eval(),
                'moves': []
            }]

        opp_move_color = get_opp_color(move_color)

        gen = board.generate_next_board(move_color)
        result = []
        lines = self.lines if deep == 0 else 1
        for move in gen:
            cand = self.dfs(
                board, opp_move_color, data, deep=deep + 1)

            result.append(cand[0])
            result[-1]['moves'].append(move)
            result.sort(
                key=lambda x: x['evaluation'], reverse=(move_color==WHITE))
            result = result[:lines]

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


class AlphaAnalyzer(Analyzer):
    name = 'AlphaAnalyzer'

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
                'evaluation': board.get_pieces_eval(),
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
    name = 'AlphaBetaAnalyzer'

    def dfs(self, board, move_color, data,
            alpha=-Analyzer.MAX_EVALUATION - 1, beta=Analyzer.MAX_EVALUATION + 1, deep=0):
        '''
        If evaluation between (alpha, beta) returns it,
        otherwise if less returns less or equal alpha
                  if more returns more or equal beta

        !!!! It always returns result of non-zero length

        Alpha-beta pruning
            if alpha and beta not passed dfs will return always true evaluation
        max_deep - 2*n for checkmate in `n` moves

        `evaluation` == True
            if players are allowed to make only takes

        TODO: (kosteev) write tests
        TODO: (kosteev) compare with simple analyzer
        '''
        data['nodes'] += 1
        if deep == self.max_deep:
            return [{
                'evaluation': board.get_pieces_eval(),
                'moves': []
            }]

        opp_move_color = get_opp_color(move_color)

        lines = self.lines if deep == 0 else 1
        result = []
        is_any_move = False
        sort_key = None
        if self.evaluation:
            # First takes
            sort_key = lambda x: (-1 if x['new_position_old_piece'] else 1)
        gen = board.generate_next_board(move_color, sort_key=sort_key)

        for move in gen:
            is_any_move = True

            if (self.evaluation and
                    not move['new_position_old_piece']):
                # Because it is sorted by takes, no more takes in gen
                try:
                    gen.send(True)
                except StopIteration:
                    pass
                break

            cand = self.dfs(
                board, opp_move_color, data,
                alpha=alpha, beta=beta, deep=deep + 1)

            result.append(cand[0])
            result[-1]['moves'].append(move)
            # XXX: sorting is stable, it will never get newer variant
            # (which can be with wrong evaluation).
            result.sort(
                key=lambda x: x['evaluation'], reverse=(move_color==WHITE))
            result = result[:lines]

            if len(result) == lines:
                if move_color == WHITE:
                    alpha = max(alpha, result[-1]['evaluation'])
                else:
                    beta = min(beta, result[-1]['evaluation'])

            # >= ? >
            # Try both and see how many nodes
            if alpha >= beta:
                try:
                    gen.send(True)
                except StopIteration:
                    pass
                break

        if not is_any_move:
            sign = color_sign(move_color)
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

        if self.evaluation:
            if not result:
                # is_any_move == True, but no takes occured
                return [{
                    'evaluation': board.get_pieces_eval(),
                    'moves': []
                }]

        return result
