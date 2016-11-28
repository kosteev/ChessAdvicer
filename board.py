from pieces import get_opp_color, PIECES, MOVES
from utils import on_board


class Board(object):
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

    def generate_next_board(
            self, move_color, check=False):
        opp_move_color = get_opp_color(move_color)

        pieces_list = []
        for position, (piece, color) in self.pieces.items():
            if color != move_color:
                continue
            pieces_list.append((position, (piece, color)))
        # XXX: should we sort by position?
        pieces_list.sort(
            key=lambda x: (PIECES[x[1][0]]['priority'], x[0]), reverse=True)

        for position, (piece, color) in pieces_list:
            for variant in self.get_piece_moves(position):
                for diff in variant:
                    new_position = (position[0] + diff[0], position[1] + diff[1])

                    if not on_board(new_position):
                        break

                    new_position_piece = self.pieces.get(new_position)
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
                        self.pieces[new_position] = (diff[2] or self.pieces[position][0], self.pieces[position][1])
                        del self.pieces[position]

                        finish = False
                        if not self.is_check(opp_move_color):
                            finish = yield {
                                'position': position,
                                'new_position': new_position,
                                'piece': piece,
                                'new_piece': self.pieces[new_position][0],
                                'is_take': True if new_position_piece else False
                            }

                        # Recover
                        self.pieces[position] = (piece, color)
                        if new_position_piece:
                            self.pieces[new_position] = new_position_piece
                        else:
                            del self.pieces[new_position]

                        if finish:
                            return

                    if last_diff:
                        break

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
