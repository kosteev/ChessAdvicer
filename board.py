import json
import random

from pieces import get_opp_color, PIECES, PROBABLE_MOVES, WHITE, PIECE_CELL_VALUE, CHECK_LINES
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

        self.material = self.get_material_eval()
        self.positional_eval = self.get_positional_eval()

    def copy(self):
        return Board(
            pieces=self.pieces.copy(),
            move_color=self.move_color,
            en_passant=self.en_passant,
            move_up_color=self.move_up_color,
            lt_screen=self.lt_screen,
            cell_size=self.cell_size
        )

    @property
    def hash(self):
        return hash(json.dumps(sorted(self.pieces.items()) + [self.move_color, self.en_passant]))

    @property
    def evaluation(self):
        return self.material + self.positional_eval / 1000.0

    def get_material_eval(self):
        '''
        pieces = {(1, 2): ('rook', 'white)}
        '''
        total = 0
        for (piece, color) in self.pieces.values():
            total += color_sign(color) * PIECES[piece]['value']

        return total

    def get_positional_eval(self):
        '''
        Returns count of probable moves.
        TODO: (kosteev) consider all chess rules
        '''
        total = 0
        for position, (piece, color) in self.pieces.items():
            total += color_sign(color) * PIECE_CELL_VALUE[piece][position]

        return total

    def generate_next_board(self, capture_sort_key=None):
        '''
        Method to generate next valid board position
            if check == True, yield if check is occured
            if check == False, first yield with moves info
        '''
        move_color = self.move_color
        opp_move_color = get_opp_color(move_color)
        sign = color_sign(move_color)

        simple_moves = []
        capture_moves = []
        for position, (piece, color) in self.pieces.items():
            if color != move_color:
                continue

            for variant in self.get_piece_probable_moves(position):
                for move in variant:
                    new_position = move['new_position']
                    new_piece = move.get('new_piece') or piece
                    captured_position = move.get('captured_position') or new_position

                    captured_piece, captured_color = self.pieces.get(captured_position, (None, None))
                    if captured_color == move_color:
                        break

                    move = {
                        'position': position,
                        'new_position': new_position,
                        'piece': piece,
                        'new_piece': new_piece,
                        'captured_position': captured_position,
                        'captured_piece': captured_piece
                    }
                    if captured_piece:
                        capture_moves.append(move)
                    else:
                        simple_moves.append(move)

                    if captured_color == opp_move_color:
                        break

        # Shuffle to make generate function not-deterministic
        random.shuffle(capture_moves)
        random.shuffle(simple_moves)
        #capture_moves.sort(key=lambda x: (x['position'], x['new_position'], x['new_piece']))
        #simple_moves.sort(key=lambda x: (x['position'], x['new_position'], x['new_piece']))

        # Sort captured moves
        if capture_sort_key is None:
            capture_sort_key = self.sort_take_by_value
        capture_moves.sort(key=capture_sort_key)

        for move in capture_moves + simple_moves:
            # Make move
            del self.pieces[move['position']]
            if move['captured_piece']:
                del self.pieces[move['captured_position']]
            self.pieces[move['new_position']] = (move['new_piece'], move_color)
            # Recalculate evaluation
            delta_material = PIECES[move['new_piece']]['value']
            delta_material -= PIECES[move['piece']]['value']
            if move['captured_piece']:
                delta_material += PIECES[move['captured_piece']]['value']
            delta_material *= sign
            self.material += delta_material
            # Recalculate probable moves
            delta_positional_eval = PIECE_CELL_VALUE[move['new_piece']][move['new_position']]
            delta_positional_eval -= PIECE_CELL_VALUE[move['piece']][move['position']]
            if move['captured_piece']:
                delta_positional_eval += \
                    PIECE_CELL_VALUE[move['captured_piece']][move['captured_position']]
            delta_positional_eval *= sign
            self.positional_eval += delta_positional_eval
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
            self.material -= delta_material
            # Return probable moves
            self.positional_eval -= delta_positional_eval
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
    def sort_take_by_value(move):
        '''
        The most valueable + by the most cheap
        '''
        captured_piece = move['captured_piece']
        return [
            -PIECES[captured_piece]['value'], PIECES[move['piece']]['value']]
