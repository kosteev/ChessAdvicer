import time
from multiprocessing import Pool, cpu_count

from board import Board
from endgame import get_syzygy_best_move
from pieces import WHITE, BLACK
from utils import color_sign


def pool_dfs_wrapper(pool_arg):
    analyzer, args, kwargs = pool_arg
    return analyzer.dfs(*args, **kwargs)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class Analyzer(object):
    def __init__(self, max_deep, evaluation_func, lines=1):
        self.max_deep = max_deep
        self.lines = lines
        self.evaluation_func = evaluation_func

    def analyze(self, board):
        stats = {
            'nodes': 0
        }
        result = self.dfs(board, stats)

        return {
            'result': result,
            'stats': stats
        }

    def board_evaluation(self, board):
        evaluation = self.evaluation_func(board)
        return [{
            'evaluation': evaluation['result']['evaluation'],
            'moves': [],
            'evaluation_moves': evaluation['result']['moves'],
            'evaluation_stats': evaluation['stats']
        }]


class SimpleAnalyzer(Analyzer):
    def dfs(self, board, stats, deep=0):
        '''
        max_deep - 2*n for checkmate in `n` moves

        TODO: (kosteev) write tests
        '''
        stats['nodes'] += 1
        if deep == self.max_deep:
            return self.board_evaluation(board)

        move_color = board.move_color

        gen = board.generate_next_board()

        result = []
        lines = self.lines if deep == 0 else 1
        for move in gen:
            cand = self.dfs(
                board, stats, deep=deep + 1)

            result.append(cand[0])
            result[-1]['moves'].append(move)
            result.sort(
                key=lambda x: x['evaluation'], reverse=(move_color==WHITE))
            result = result[:lines]

        sign = color_sign(move_color)
        if not result:
            if board.is_check(opposite=True):
                # Checkmate
                result = [{
                    'evaluation': -sign * (Board.MAX_EVALUATION - deep),
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
    def dfs(self, board, stats, alpha=None, deep=0):
        '''
        alpha - to reduce brute force
            if alpha is None dfs will return always list not 0-length
        max_deep - 2*n for checkmate in `n` moves

        TODO: (kosteev) write tests
        '''
        stats['nodes'] += 1
        if deep == self.max_deep:
            return self.board_evaluation(board)

        move_color = board.move_color

        gen = board.generate_next_board()

        result = []
        lines = self.lines if deep == 0 else 1
        for move in gen:
            cand = self.dfs(
                board, stats,
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
            if board.is_check(opposite=True):
                # Checkmate
                result = [{
                    'evaluation': -sign * (Board.MAX_EVALUATION - deep),
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
    def __init__(self, *args, **kwargs):
        max_time = kwargs.pop('max_time', 999999)
        self.max_time = max_time

        super(AlphaBetaAnalyzer, self).__init__(*args, **kwargs)

    @classmethod
    def pool(cls):
        if not hasattr(cls, '_pool'):
            cls._pool = Pool(processes=cpu_count())

        return cls._pool

    def analyze(self, board):
        self.analyze_launch_time = time.time()

        # syzygy_best_move = get_syzygy_best_move(board)
        # Temporary commented
        syzygy_best_move = None
        if syzygy_best_move is None:
            result = self.dfs(board)
        else:
            result = [{
                'evaluation': syzygy_best_move['evaluation'],
                'moves': syzygy_best_move['moves']
            }]

        stats = {'nodes': 1}
        return {
            'result': result,
            'stats': stats
        }

    def dfs(self, board, alpha=-Board.MAX_EVALUATION - 1, beta=Board.MAX_EVALUATION + 1, deep=0):
        '''
        !!!! This function should be multi-thread safe.

        If evaluation between (alpha, beta) returns it,
        otherwise if less returns less or equal alpha
                  if more returns more or equal beta

        !!!! It always returns result of non-zero length

        Alpha-beta pruning
            if alpha and beta not passed dfs will return always true evaluation
        max_deep - 2*n for checkmate in `n` moves

        TODO: (kosteev) write tests
        TODO: (kosteev) compare with simple analyzer
        '''
        if time.time() - self.analyze_launch_time > self.max_time:
            if alpha >= -Board.MAX_EVALUATION:
                return [{
                    'evaluation': alpha,  # Return evaluation that will not affect result
                    'moves': []
                }]

            if beta <= Board.MAX_EVALUATION:
                return [{
                    'evaluation': beta,  # Return evaluation that will not affect result
                    'moves': []
                }]

        if deep == self.max_deep:
            return self.board_evaluation(board)

        move_color = board.move_color

        lines = self.lines if deep == 0 else 1
        result = []
        is_any_move = False

        gen = board.generate_next_board()
        if deep == 0:
            pool_args = []
            moves = []
            for move in gen:
                is_any_move = True
                args = (board.copy(), )
                kwargs = {
                    'deep': deep + 1
                }
                pool_args.append((self, args, kwargs))
                moves.append(move)

            # TODO: consider results in already runned
            threads = cpu_count()
            for ch_ind, chunk in enumerate(chunks(pool_args, threads)):
                for _ in chunk:
                    _[2]['alpha'] = alpha
                    _[2]['beta'] = beta
                for ind, cand in enumerate(self.pool().map(pool_dfs_wrapper, chunk)):
                    result.append(cand[0])
                    result[-1]['moves'].append(moves[ch_ind * threads + ind])
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

                    if alpha >= beta:
                        break
        else:
            for move in gen:
                is_any_move = True

                cand = self.dfs(
                    board, alpha=alpha, beta=beta, deep=deep + 1)

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

                if alpha >= beta:
                    break

        try:
            gen.send(True)
        except StopIteration:
            pass

        if not is_any_move:
            sign = color_sign(move_color)
            if board.is_check(opposite=True):
                # Checkmate
                result = [{
                    'evaluation': -sign * (Board.MAX_EVALUATION - deep),
                    'moves': []
                }]
            else:
                # Draw
                result = [{
                    'evaluation': 0,
                    'moves': []
                }]

        return result
