import random

from pieces import get_opp_color, PIECES, MOVES
from utils import on_board, color_sign


class Board(object):
    MAX_EVALUATION = 1000
    # 999 - checkmate in one move, 998 - ...

    SORT_BY_TAKE_VALUE = staticmethod(lambda x: (
        -1 if x['new_position_old_piece'] else 1,
        -PIECES[x['new_position_old_piece'][0]]['value'] if x['new_position_old_piece'] else 0))

    def __init__(self, pieces, move_up_color, move_color, xy):
        '''
            `pieces` - dict with pieces
                pieces = {(1, 2): ('rook', 'white)}
            `move_up_color` - color of side whose goes up
            `move_color` - color of side to move
            `xy` - coordinates of board position on screen
        '''
        self.pieces = pieces
        self.move_up_color = move_up_color
        self.move_color = move_color
        self.xy = xy

    def get_pieces_eval(self):
        '''
        pieces = {(1, 2): ('rook', 'white)}
        '''
        total = 0
        for (piece, color) in self.pieces.values():
            total += color_sign(color) * PIECES[piece]['value']

        return total

    def generate_next_board(
            self, move_color, check=False, sort_key=None):
        opp_move_color = get_opp_color(move_color)

        moves = []
        for position, (piece, color) in self.pieces.items():
            if color != move_color:
                continue

            for variant in self.get_piece_moves(position):
                for diff in variant:
                    new_position = (position[0] + diff[0], position[1] + diff[1])

                    if not on_board(new_position):
                        break

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
                            'new_piece': diff[2] or piece,
                            'new_position_old_piece': new_position_old_piece
                        })

                    if last_diff:
                        break

        random.shuffle(moves)
        if sort_key is None:
            sort_key = self.SORT_BY_TAKE_VALUE
        moves.sort(key=sort_key)

        for move in moves:
            # Make move
            self.pieces[move['new_position']] = (move['new_piece'], move_color)
            del self.pieces[move['position']]

            finish = False
            if not self.is_check(opp_move_color):
                finish = yield move

            # Recover
            self.pieces[move['position']] = (move['piece'], move_color)
            if move['new_position_old_piece']:
                self.pieces[move['new_position']] = move['new_position_old_piece']
            else:
                del self.pieces[move['new_position']]

            if finish:
                return

    def get_piece_moves(self, position):
        '''
            1. By rules ( + on board)
            2. Do not pass someone on the way, except finish with opposite color
            3. Do not make own king under check

            ???
            1. on passan
            2. 0-0 | 0-0-0
        '''
        piece, move_color = self.pieces[position]

        moves = []
        if piece != 'pawn':
            moves = MOVES[piece]
        else:
            opp_move_color = get_opp_color(move_color)

            if move_color == self.move_up_color:
                sign = -1
            else:
                sign = 1

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
                    new_position = (position[0] + x, position[1] + sign)
                    if (new_position in self.pieces and
                            self.pieces[new_position][1] == opp_move_color):
                        moves.append([(x, sign, promote_piece)])

                # Second move forward
                # Check if position is empty, to avoid treating as take
                if (position[0], position[1] + sign) not in self.pieces:
                    forward_moves = [(0, sign, promote_piece)]
                    if ((position[0], position[1] + 2 * sign) not in self.pieces and
                            position[1] - sign in [0, 7]):
                        # Move on two steps
                        forward_moves.append((0, 2 * sign, promote_piece))

                    moves.append(forward_moves)

        return moves

    def is_check(self, move_color):
        '''
        Determines if check is by move_color to opposite color
        '''
        check = False
        for _ in self.generate_next_board(move_color, check=True):
            check = True
            # Allow to end this loop to release generator

        return check
