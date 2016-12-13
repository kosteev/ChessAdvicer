import json
import random

from pieces import get_opp_color, PIECES, PROBABLE_MOVES, WHITE, COUNT_OF_PROBABLE_MOVES, CHECK_LINES, on_board
from utils import color_sign


DIRECTIONS = {
    0: [(0, x) for x in xrange(1, 10)],
    1: [(x, x) for x in xrange(1, 10)],
    2: [(x, 0) for x in xrange(1, 10)],
    3: [(x, -x) for x in xrange(1, 10)],
    4: [(0, -x) for x in xrange(1, 10)],
    5: [(-x, -x) for x in xrange(1, 10)],
    6: [(-x, 0) for x in xrange(1, 10)],
    7: [(-x, x) for x in xrange(1, 10)]
}
PIECE_DIRECTIONS = {
    'rook': {
        'directions': lambda _: {0, 2, 4, 6},
    },
    'bishop': {
        'directions': lambda _: {1, 3, 5, 7},
    },
    'queen': {
        'directions': lambda _: {0, 1, 2, 3, 4, 5, 6, 7},
    },
    'king': {
        'directions': lambda _: {0, 1, 2, 3, 4, 5, 6, 7},
        'short': True
    },
    'pawn': {
        'directions': lambda color: {1, 7} if color == WHITE else {3, 5},
        'short': True
    },
    'knight': {
        'directions': lambda _: set()
    }
}


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
        self.init_pieces(pieces)
        self.move_color = move_color
        self.en_passant = en_passant

        self.move_up_color = move_up_color
        self.lt_screen = lt_screen
        self.cell_size = cell_size

        self.evaluation = self.get_pieces_eval()
        self.probable_moves_count = self.get_probable_moves_count()

    def init_pieces(self, pieces):
        '''
        Inits pieces, dgraph.
        Adds to dgraph all border cells with appropriate direction cells.
        '''
        self.pieces = {}
        self.dgraph = {}
        self.beaten_count = {}

        border_cells = []
        border_cells += [(c, -1) for c in xrange(8)]
        border_cells += [(c, 8) for c in xrange(8)]
        border_cells += [(-1, c) for c in xrange(8)]
        border_cells += [(8, c) for c in xrange(8)]
        border_cells += [(-1, -1), (-1, 8), (8, -1), (8, 8)]
        for cell in border_cells:
            self.dgraph[cell] = {}
            for direction, line in DIRECTIONS.items():
                for diff in line:
                    line_cell = (cell[0] + diff[0], cell[1] + diff[1])
                    if not on_board(line_cell):
                        self.dgraph[cell][direction] = line_cell
                        break
                else:
                    raise IndexError('Not found cell for {}, {}'.format(cell, direction))

        for position, (piece, color) in pieces.items():
            self.put_piece(position, piece, color)

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

    def get_beaten_cells_count(self, print_=False):
        total = 0
        for position, (_, color) in self.pieces.items():
            total += color_sign(color) * sum(self.beaten_count[position].values())
#             if print_:
#                 print position, color_sign(color) * self.beaten_cells_by_piece(position)

        return total

    def generate_next_board(self, capture_sort_key=None):
        '''
        Method to generate next valid board position
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

        # Sort captured moves
        if capture_sort_key is None:
            capture_sort_key = self.sort_take_by_value
        capture_moves.sort(key=capture_sort_key)

        for move in capture_moves + simple_moves:
            # Make move
            # del self.pieces[move['position']]
            self.remove_piece(move['position'])
            if move['captured_piece']:
                # del self.pieces[move['captured_position']]
                self.remove_piece(move['captured_position'])
            # self.pieces[move['new_position']] = (move['new_piece'], move_color)
            self.put_piece(move['new_position'], move['new_piece'], move_color)

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
            # del self.pieces[move['new_position']]
            self.remove_piece(move['new_position'])
            if move['captured_piece']:
                # self.pieces[move['captured_position']] = (move['captured_piece'], opp_move_color)
                self.put_piece(move['captured_position'], move['captured_piece'], opp_move_color)
            # self.pieces[move['position']] = (move['piece'], move_color)
            self.put_piece(move['position'], move['piece'], move_color)

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
    def sort_take_by_value(move):
        '''
        The most valueable + by the most cheap
        '''
        captured_piece = move['captured_piece']
        return [
            -PIECES[captured_piece]['value'], PIECES[move['piece']]['value']]

    def put_piece(self, put_position, put_piece, put_color):
        '''
        Place piece on the board, makes all necessary recalculations
        '''
        if put_position in self.pieces:
            raise ValueError('Some piece is already on this position - {}'.format(put_position))

        self.dgraph[put_position] = {}
        self.beaten_count[put_position] = {}
        self.pieces[put_position] = (put_piece, put_color)

#         # Iterate only over first 4 directions, other directions will be considered automatically
#         for direction in xrange(4):
#             opp_direction = direction + 4
#             for diff in DIRECTIONS[direction]:
#                 d_position = (put_position[0] + diff[0], put_position[1] + diff[1])
#                 if d_position not in self.dgraph:
#                     continue
# 
#                 opp_position = self.dgraph[d_position][opp_direction]
# 
#                 # Update dgraph for put_position
#                 self.dgraph[put_position][direction] = d_position
#                 self.dgraph[put_position][opp_direction] = opp_position
# 
#                 # Update dgraph for d_position/opp_position
#                 self.dgraph[d_position][opp_direction] = put_position
#                 self.dgraph[opp_position][direction] = put_position
# 
#                 # Update beaten cells for put_position/d_position
#                 self.update_beaten_cells(put_position, direction, d_position)
#                 self.update_beaten_cells(d_position, opp_direction, put_position)
# 
#                 # Update beaten cells for put_position/opp_position
#                 self.update_beaten_cells(put_position, opp_direction, opp_position)
#                 self.update_beaten_cells(opp_position, direction, put_position)
#                 break

    def remove_piece(self, remove_position):
        '''
        Removes piece from the board, makes all necessary recalculations
        '''
#         for direction in xrange(4):
#             opp_direction = direction + 4
#             d_position = self.dgraph[remove_position][direction]
#             opp_position = self.dgraph[remove_position][opp_direction]
# 
#             self.dgraph[d_position][opp_direction] = opp_position
#             self.dgraph[opp_position][direction] = d_position
# 
#             # Update beaten cells for d_position/opp_position
#             self.update_beaten_cells(d_position, opp_direction, opp_position)
#             self.update_beaten_cells(opp_position, direction, d_position)

        del self.dgraph[remove_position]
        del self.beaten_count[remove_position]
        del self.pieces[remove_position]

    def update_beaten_cells(self, position, direction, opp_position):
        piece, color = self.pieces.get(position, (None, None))
        if piece:
            if direction in PIECE_DIRECTIONS[piece]['directions'](color):
                distance = abs(position[0] - opp_position[0])
                if distance == 0:
                    distance = abs(position[1] - opp_position[1])
                if PIECE_DIRECTIONS[piece].get('short'):
                    distance = min(2, distance)
                self.beaten_count[position][direction] = distance - 1
