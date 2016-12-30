import sys
import time
import traceback
from multiprocessing import Pool, cpu_count, Manager

from board import Board
from pieces import WHITE, BLACK
from utils import color_sign


def pool_dfs_wrapper(pool_arg):
    '''
    Wraps dfs in try/except, multiprocessing doesn't provide actual stack trace.
    '''
    analyzer, args, kwargs = pool_arg
    try:
        return analyzer.dfs(*args, **kwargs)
    except Exception:
        raise Exception("".join(traceback.format_exception(*sys.exc_info())))


class Analyzer(object):
    def __init__(self, max_deep, evaluation_func, lines=1):
        '''
        max_deep - 2*n for checkmate in `n` moves
        '''
        if max_deep <= 0:
            raise ValueError('Max deep should be more or equal than one')

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
        stats['nodes'] += 1
        if deep == self.max_deep:
            return self.board_evaluation(board)

        move_color = board.move_color

        result = []
        lines = self.lines if deep == 0 else 1
        for move in board.get_board_moves():
            revert_info = board.make_move(move)
            if revert_info is None:
                continue

            cand = self.dfs(
                board, stats, deep=deep + 1)
            board.revert_move(revert_info)

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
        '''
        stats['nodes'] += 1
        if deep == self.max_deep:
            return self.board_evaluation(board)

        move_color = board.move_color

        result = []
        lines = self.lines if deep == 0 else 1
        for move in board.get_board_moves():
            revert_info = board.make_move(move)
            if revert_info is None:
                continue

            cand = self.dfs(
                board, stats,
                alpha=result[-1]['evaluation'] if len(result) == lines else None, deep=deep + 1)
            board.revert_move(revert_info)

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
        self.max_time = kwargs.pop('max_time', 999999)
        self.max_deep_captures = kwargs.pop('max_deep_captures', 0)
        self.max_deep_one_capture = kwargs.pop('max_deep_one_capture', 0)

        super(AlphaBetaAnalyzer, self).__init__(*args, **kwargs)

    @classmethod
    def pool(cls):
        if not hasattr(cls, '_pool'):
            cls._pool = Pool(processes=cpu_count())

        return cls._pool

    @classmethod
    def manager(cls):
        # Initialize pool
        # ??? Should we do it?
        cls.pool()
        if not hasattr(cls, '_manager'):
            cls._manager = Manager()

        return cls._manager

    def analyze(self, board, alpha=-Board.MAX_EVALUATION - 1, beta=Board.MAX_EVALUATION + 1,
                moves_to_consider=None):
        '''
        If evaluation between (alpha, beta) returns it,
        otherwise if less returns less or equal alpha
                  if more returns more or equal beta

        Alpha-beta pruning
            if alpha and beta not passed it will return always true evaluation
        '''
        result, _ = self.dfs_parallel(
            board, alpha, beta, time.time(), moves_to_consider=moves_to_consider)

        stats = {'nodes': 1}
        return {
            'result': result,
            'stats': stats
        }

    def dfs(self, board, alpha, beta, analyze_launch_time, moves_to_consider=None,
            deep=0, parent_alpha_beta=None, parent_ind=None):
        '''
        !!!! This function should be multi-thread safe.
        !!!! It always returns result of non-zero length

        `moves_to_consider` - moves to consider, if None than all valid moves are considered
        '''
        if time.time() - analyze_launch_time > self.max_time:
            # If alpha or beta is determined here, than there is calculated one variant already
            if alpha >= -Board.MAX_EVALUATION:
                return [{
                    'evaluation': alpha,  # Return evaluation that will not affect result
                    'moves': []
                }], parent_ind

            if beta <= Board.MAX_EVALUATION:
                return [{
                    'evaluation': beta,  # Return evaluation that will not affect result
                    'moves': []
                }], parent_ind

        result = []
        move_color = board.move_color
        lines = self.lines if deep == 0 else 1
        is_any_move = False

        if deep >= self.max_deep:
            result = self.board_evaluation(board)
            is_any_move = True
            if deep == self.max_deep + self.max_deep_captures + self.max_deep_one_capture:
                moves = []
            else:
                # Allow only takes
                moves = board.get_board_captures(capture_sort_key=Board.sort_take_by_value)
        else:
            moves = board.get_board_moves(
                capture_sort_key=Board.sort_take_by_value) if moves_to_consider is None else moves_to_consider

        for move in moves:
            revert_info = board.make_move(move)
            if revert_info is None:
                continue

            is_any_move = True
            cand, _ = self.dfs(
                board, alpha, beta, analyze_launch_time, deep=deep + 1)
            board.revert_move(revert_info)

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

            # Refresh alpha/beta according to parent
            if parent_alpha_beta is not None:
                if move_color == WHITE:
                    beta = parent_alpha_beta.value
                else:
                    alpha = parent_alpha_beta.value

            # Here is the first time it could happen
            if alpha >= beta:
                break

            if deep >= self.max_deep + self.max_deep_captures:
                # Consider only one take
                break

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

        return result, parent_ind

    def dfs_parallel(self, board, alpha, beta, analyze_launch_time, moves_to_consider=None):
        '''
        !!!! It always returns result of non-zero length

        `moves_to_consider` - moves to consider, if None than all valid moves are considered
        '''
        move_color = board.move_color
        result = []
        is_any_move = False

        pool_args = []
        moves = []
        board_moves = board.get_board_moves() if moves_to_consider is None else moves_to_consider
        if move_color == WHITE:
            parent_alpha_beta = self.manager().Value('i', alpha)
        else:
            parent_alpha_beta = self.manager().Value('i', beta)

        for move in board_moves:
            revert_info = board.make_move(move)
            if revert_info is None:
                continue
            is_any_move = True

            args = (board.copy(), alpha, beta, analyze_launch_time)
            kwargs = {
                'deep': 1,
                'parent_alpha_beta': parent_alpha_beta,
                'parent_ind': len(moves)
            }
            pool_args.append((self, args, kwargs))
            moves.append(move)

            board.revert_move(revert_info)

        for cand, ind in self.pool().imap_unordered(
                pool_dfs_wrapper, pool_args):
            result.append(cand[0])
            result[-1]['moves'].append(moves[ind])
            # XXX: sorting is stable, it will never get newer variant
            # (which can be with wrong evaluation).
            result.sort(
                key=lambda x: x['evaluation'], reverse=(move_color==WHITE))
            result = result[:self.lines]

            if len(result) == self.lines:
                if move_color == WHITE:
                    parent_alpha_beta.value = max(parent_alpha_beta.value, result[-1]['evaluation'])
                else:
                    parent_alpha_beta.value = min(parent_alpha_beta.value, result[-1]['evaluation'])

            # Here is the first time it could happen
            if move_color == WHITE:
                if parent_alpha_beta.value >= beta:
                    break
            else:
                if alpha >= parent_alpha_beta.value:
                    break

        if not is_any_move:
            sign = color_sign(move_color)
            if board.is_check(opposite=True):
                # Checkmate
                result = [{
                    'evaluation': -sign * Board.MAX_EVALUATION,
                    'moves': []
                }]
            else:
                # Draw
                result = [{
                    'evaluation': 0,
                    'moves': []
                }]

        return result, None
