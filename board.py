import json
import random

from pieces import get_opp_color, PIECES, PROBABLE_MOVES, WHITE, COUNT_OF_PROBABLE_MOVES
from utils import color_sign


class Board(object):
    MAX_EVALUATION = 1000
    # 999 - checkmate in one move, 998 - ...

    def __init__(self, pieces, move_color, move_up_color=WHITE, lt_screen=None, cell_size=None):
        '''
            `pieces` - dict with pieces
                pieces = {(1, 2): ('rook', 'white)}
            `move_up_color` - color of side who goes up, just for display purpose
            `lt_screen` - coordinates of board left-top position on the screen, for gui library
            `cell_size` - size of cell, for gui library
        '''
        self.pieces = pieces
        self.move_color = move_color
        self.move_up_color = move_up_color
        self.lt_screen = lt_screen
        self.cell_size = cell_size

        self.evaluation = self.get_pieces_eval()

    def hash(self):
        return hash(json.dumps(sorted(self.pieces.items()) + [self.move_color]))

    def get_pieces_eval(self):
        '''
        pieces = {(1, 2): ('rook', 'white)}
        '''
        total = 0
        for (piece, color) in self.pieces.values():
            total += color_sign(color) * PIECES[piece]['value']

        return total

    def get_probable_moves_count(self):
        '''
        Returns count of probable moves.
        TODO: (kosteev) consider all chess rules
        '''
        total = 0
        for position, (piece, color) in self.pieces.items():
            if piece == 'pawn':
                probable_moves = 1 if position[0] in [0, 7] else 2
            else:
                probable_moves = COUNT_OF_PROBABLE_MOVES[piece][position]
            total += color_sign(color) * probable_moves

        return total

    def generate_next_board(
            self, check=False, sort_key=None):
        '''
        Method to generate next valid board position
            if check == True, yield if check is occured
            if check == False, first yield with moves info
        '''
        move_color = self.move_color
        opp_move_color = get_opp_color(move_color)
        sign = color_sign(move_color)

        moves = []
        for position, (piece, color) in self.pieces.items():
            if color != move_color:
                continue

            for variant in self.get_piece_probable_moves(position):
                for move in variant:
                    new_position = move[:-1]

                    new_position_old_piece = self.pieces.get(new_position)
                    last_diff = False
                    if new_position_old_piece:
                        if new_position_old_piece[1] == move_color:
                            break
                        else:
                            last_diff = True

                    if check:
                        if new_position_old_piece == ('king', opp_move_color):
                            yield
                            return
                    else:
                        moves.append({
                            'position': position,
                            'new_position': new_position,
                            'piece': piece,
                            'new_piece': move[2] or piece,
                            'new_position_old_piece': new_position_old_piece
                        })

                    if last_diff:
                        break

        if check:
            return

        random.shuffle(moves)
        if sort_key is None:
            sort_key = self.sort_by_take_value
        moves.sort(key=sort_key)

        for move in moves:
            # Make move
            self.pieces[move['new_position']] = (move['new_piece'], move_color)
            del self.pieces[move['position']]
            # Recalculate evaluation
            delta = PIECES[move['new_piece']]['value'] - PIECES[move['new_piece']]['value']
            if move['new_position_old_piece']:
                delta += PIECES[move['new_position_old_piece'][0]]['value']
            delta *= sign
            self.evaluation += delta
            # Move color
            self.move_color = opp_move_color

            finish = False
            if not self.is_check():
                finish = yield move

            # Recover
            self.pieces[move['position']] = (move['piece'], move_color)
            if move['new_position_old_piece']:
                self.pieces[move['new_position']] = move['new_position_old_piece']
            else:
                del self.pieces[move['new_position']]
            # Retrun evaluation
            self.evaluation -= delta
            # Move color
            self.move_color = move_color

            if finish:
                return

    def get_piece_probable_moves(self, position):
        '''
        Returns probable piece moves
        1. By rules ( + on board) - PROBABLE_MOVES
        2. Do not pass someone on the way, except finish with opposite color
        3. Do not make own king under check

        ???
        1. on passan
        2. 0-0 | 0-0-0
        '''
        piece, move_color = self.pieces[position]

        probable_moves = []
        if piece != 'pawn':
            probable_moves = PROBABLE_MOVES[piece][position]
        else:
            opp_move_color = get_opp_color(move_color)
            sign = color_sign(move_color)

            promote_pieces = []
            if position[1] + sign in [0, 7]:
                # Last rank
                for piece in PIECES:
                    if piece not in ['king', 'pawn']:
                        promote_pieces.append(piece)
            else:
                promote_pieces.append(None)

            for promote_piece in promote_pieces:
                # First on side
                for x in [-1, 1]:
                    probable_move = (position[0] + x, position[1] + sign, promote_piece)
                    if (probable_move[:-1] in self.pieces and
                            self.pieces[probable_move[:-1]][1] == opp_move_color):
                        probable_moves.append([probable_move])

                # Second move forward
                # Check if position is empty, to avoid treating as take
                probable_move = (position[0], position[1] + sign, promote_piece)
                if probable_move[:-1] not in self.pieces:
                    forward_moves = [probable_move]
                    probable_move = (position[0], position[1] + 2 * sign, promote_piece)
                    if (probable_move[:-1] not in self.pieces and
                            position[1] - sign in [0, 7]):
                        # Move on two steps
                        forward_moves.append(probable_move)

                    probable_moves.append(forward_moves)

        return probable_moves

    def is_check(self, opposite=False):
        '''
        Determines if check is by self.move_color to opposite color
            `opposite` == True, check for the opposites side
        '''
        check = False
        if opposite:
            self.move_color = get_opp_color(self.move_color)

        for _ in self.generate_next_board(check=True):
            check = True
            # Allow to end this loop to release generator

        if opposite:
            self.move_color = get_opp_color(self.move_color)

        return check

    @staticmethod
    def sort_by_take_value(move):
        '''
        Take+the most valueable+by the most cheap
        '''
        new_position_old_piece = move.get('new_position_old_piece')
        if new_position_old_piece:
            return [
                -1, -PIECES[new_position_old_piece[0]]['value'], PIECES[move['piece']]['value']]
        return [1]
