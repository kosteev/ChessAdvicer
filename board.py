import json
import random

from pieces import get_opp_color, PIECES, PROBABLE_MOVES, WHITE, COUNT_OF_PROBABLE_MOVES, CHECK_LINES
from utils import color_sign


class Board(object):
    MAX_EVALUATION = 1000
    # 999 - checkmate in one move, 998 - ...

    def __init__(self, pieces, move_color, en_passant, move_up_color=WHITE, lt_screen=None, cell_size=None):
        '''
            `pieces` - dict with pieces
                pieces = {(1, 2): ('rook', 'white)}
            `move_up_color` - color of side who goes up, just for display purpose
            `lt_screen` - coordinates of board left-top position on the screen, for gui library
            `cell_size` - size of cell, for gui library
        '''
        self.pieces = pieces
        self.move_color = move_color
        self.en_passant = en_passant
        self.move_up_color = move_up_color
        self.lt_screen = lt_screen
        self.cell_size = cell_size

        self.evaluation = self.get_pieces_eval()
        self.probable_moves_count = self.get_probable_moves_count()

    @property
    def hash(self):
        return hash(json.dumps(sorted(self.pieces.items()) + [self.move_color, self.en_passant]))

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
            total += color_sign(color) * COUNT_OF_PROBABLE_MOVES[piece][position]

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
                    new_position = move['new_position']
                    new_piece = move.get('new_piece') or piece
                    captured_position = move.get('captured_position') or new_position

                    captured_piece, captured_color = self.pieces.get(captured_position, (None, None))
                    last_diff = False
                    if captured_piece:
                        if captured_color == move_color:
                            break
                        else:
                            last_diff = True

                    if check:
                        if captured_piece == 'king':
                            yield
                            return
                    else:
                        moves.append({
                            'position': position,
                            'new_position': new_position,
                            'piece': piece,
                            'new_piece': new_piece,
                            'captured_position': captured_position,
                            'captured_piece': captured_piece
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
            del self.pieces[move['position']]
            if move['captured_piece']:
                del self.pieces[move['captured_position']]
            self.pieces[move['new_position']] = (move['new_piece'], move_color)
            # Recalculate evaluation
            delta_eval = PIECES[move['new_piece']]['value']
            delta_eval -= PIECES[move['piece']]['value']
            if move['captured_piece']:
                delta_eval += PIECES[move['captured_piece']]['value']
            delta_eval *= sign
            self.evaluation += delta_eval
            # Recalculate probable moves
            delta_prob_moves = COUNT_OF_PROBABLE_MOVES[move['new_piece']][move['new_position']]
            delta_prob_moves -= COUNT_OF_PROBABLE_MOVES[move['piece']][move['position']]
            if move['captured_piece']:
                delta_prob_moves += \
                    COUNT_OF_PROBABLE_MOVES[move['captured_piece']][move['captured_position']]
            delta_prob_moves *= sign
            self.probable_moves_count += delta_prob_moves
            # Move color
            self.move_color = opp_move_color
            # En passant
            old_en_passant = self.en_passant
            self.en_passant = None
            if (move['piece'] == 'pawn' and
                    abs(move['new_position'][1] - move['position'][1]) == 2):
                self.en_passant = (move['position'][0], (move['new_position'][1] + move['position'][1]) / 2)


            finish = False
            if not self.is_check():
                finish = yield move


            # Recover
            del self.pieces[move['new_position']]
            if move['captured_piece']:
                self.pieces[move['captured_position']] = (move['captured_piece'], opp_move_color)
            self.pieces[move['position']] = (move['piece'], move_color)
            # Retrun evaluation
            self.evaluation -= delta_eval
            # Return probable moves
            self.probable_moves_count -= delta_prob_moves
            # Move color
            self.move_color = move_color
            # Return en passant
            self.en_passant = old_en_passant

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
                # Firstly, on side
                for x in [-1, 1]:
                    probable_move = {
                        'new_position': (position[0] + x, position[1] + sign),
                        'new_piece': promote_piece
                    }
                    if (probable_move['new_position'] in self.pieces and
                            self.pieces[probable_move['new_position']][1] == opp_move_color):
                        probable_moves.append([probable_move])
                    if probable_move['new_position'] == self.en_passant:
                        probable_move['captured_position'] = (position[0] + x, position[1])
                        probable_moves.append([probable_move])

                # Secondly, move forward
                # Check if position is empty, to avoid treating as take
                probable_move = {
                    'new_position': (position[0], position[1] + sign),
                    'new_piece': promote_piece
                }
                if probable_move['new_position'] not in self.pieces:
                    forward_moves = [probable_move]
                    probable_move = {
                        'new_position': (position[0], position[1] + 2 * sign),
                        'new_piece': promote_piece
                    }
                    if (probable_move['new_position'] not in self.pieces and
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
        check_color, checked_color = self.move_color, get_opp_color(self.move_color)
        if opposite:
            check_color, checked_color = checked_color, check_color

        # Find king of side to check
        king_cell = None
        for cell, (piece, color) in self.pieces.items():
            if (color == checked_color
                    and piece == 'king'):
                king_cell = cell
                break

        if king_cell:
            for line in CHECK_LINES[checked_color][king_cell]:
                for cell_info in line:
                    piece, color = self.pieces.get(cell_info['cell'], (None, None))
                    if piece:
                        if (color == check_color and
                                piece in cell_info['pieces']):
                            return True
                        break

        return False

    @staticmethod
    def sort_by_take_value(move):
        '''
        Take+the most valueable+by the most cheap
        '''
        captured_piece = move.get('captured_piece')
        if captured_piece:
            return [
                -1, -PIECES[captured_piece]['value'], PIECES[move['piece']]['value']]
        return [1]
