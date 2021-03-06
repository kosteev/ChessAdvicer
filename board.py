import json
import random

from pieces import get_opp_color, PIECES, PROBABLE_MOVES, WHITE, PIECE_CELL_ACTIVENESS, BEAT_LINES, \
    get_castles, get_castle_id, LINE_TYPES, LINES_INFO, NEXT_CELL, CELL_TO_LINE_ID, LINE_TYPE_LT, \
    FREE_MOVES, PROMOTION_PIECES
from utils import color_sign, update_castles


class Board(object):
    MAX_EVALUATION = 1000
    # 999 - checkmate in one move, 998 - ...

    def __init__(self, pieces, move_color, en_passant=None, castles=[],
                 move_up_color=None, lt_screen=None, cell_size=None):
        '''
            `pieces` - dict with pieces
                pieces = {(1, 2): ('rook', 'white)}
            `move_up_color` - color of side who goes up, just for display purpose
            `lt_screen` - coordinates of board left-top position on the screen, for gui library
            `cell_size` - size of cell, for gui library
        '''
        # Init castles
        if not castles:
            castles = get_castles()

        self.pieces = pieces
        self.masks = {}
        for line_type in LINE_TYPES:
            self.masks[line_type] = {
                x: 0
                for x in xrange(15)
            }
        for position in self.pieces.keys():
            self.update_mask_add(position)

        self.move_color = move_color
        self.en_passant = en_passant
        self.castles = castles

        self.move_up_color = move_up_color
        self.lt_screen = lt_screen
        self.cell_size = cell_size

    def copy(self):
        return Board(
            pieces=self.pieces.copy(),
            move_color=self.move_color,
            en_passant=self.en_passant,
            castles=list(self.castles), # TODO: make here bug and check
            move_up_color=self.move_up_color,
            lt_screen=self.lt_screen,
            cell_size=self.cell_size
        )

    @staticmethod
    def pieces_hash(pieces):
        return hash(json.dumps(sorted(pieces.items())))

    @property
    def hash(self):
        # XXX: Maybe use here hash(fen)
        return hash(json.dumps(
            [Board.pieces_hash(self.pieces)] +
            self.castles + [self.move_color, self.en_passant]))

    def evaluation_params(self):
        '''
        - material
        - development
        - center
        - activeness
        - space
        - king safety
        '''
        material = [0, 0]
        development = [0, 0]
        center = [0, 0]
        activeness = [0, 0]
        space = [0, 0]
        king_safety = [0, 0]

        stage = 0
        if len(self.pieces) <= 16:
            stage = 2
        elif len(self.pieces) <= 24:
            stage = 1

        for position, (piece, color) in self.pieces.items():
            ind = 0 if color == WHITE else 1
            material[ind] += PIECES[piece]['value']
            activeness[ind] += PIECE_CELL_ACTIVENESS[piece][position]

            if piece == 'pawn':
                if 3 <= position[0] <= 4:
                    if ind == 0:
                        if position[1] == 4:
                            center[ind] += 7
                        elif position[1] == 3:
                            center[ind] += 15
                        elif position[1] == 2:
                            center[ind] += 7
                    else:
                        if position[1] == 3:
                            center[ind] += 7
                        if position[1] == 4:
                            center[ind] += 15
                        elif position[1] == 5:
                            center[ind] += 7
#             elif piece == 'king':
#                 king_safety[ind] = (7 - position[1]) if ind == 0 else position[1]
#                 king_safety[ind] *= 10

        engine_eval = 0
        if self.move_up_color:
            engine_eval += 2 * color_sign(self.move_up_color) * len(self.pieces)

        if stage <= 1:
            evaluation = material[0] - material[1] + \
                (engine_eval + \
                 activeness[0] - activeness[1] + \
                 center[0] - center[1]) / 1000.0
        else:
            evaluation = material[0] - material[1] + \
                (engine_eval + \
                 activeness[0] - activeness[1]) / 1000.0

        return {
            'material': material,
            'development': development,
            'center': center,
            'activeness': activeness,
            'space': space,
            'king_safety': king_safety,
            'engine_eval': engine_eval,
            'evaluation': evaluation
        }

    @property
    def evaluation(self):
        return self.evaluation_params()['evaluation']

    def get_board_moves(self, capture_sort_key=None):
        '''
        Returns current valid moves.
        Checks are not considered.
        '''
        for move in self.get_board_captures(capture_sort_key=capture_sort_key):
            yield move

        for move in self.get_board_simple_moves():
            yield move

    def get_board_moves_old(self, capture_sort_key=None):
        '''
        Returns current valid moves.
        Checks are not considered.
        '''
        move_color = self.move_color
        opp_move_color = get_opp_color(move_color)

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
        # capture_moves.sort(key=lambda x: (x['position'], x['new_position'], x['new_piece']))
        # simple_moves.sort(key=lambda x: (x['position'], x['new_position'], x['new_piece']))

        # Sort captured moves
        if capture_sort_key is None:
            capture_sort_key = self.sort_take_by_value
        capture_moves.sort(key=capture_sort_key)

#         if sorted(capture_moves + simple_moves) != sorted(self.get_board_moves_new(capture_sort_key)):
#             print_board(self)
#             print capture_moves
#             print simple_moves
#             raise

        return capture_moves + simple_moves

    def make_move(self, move):
        '''
        Make move on board.
        Returns dict with info to restore board position.
        If move is not valid (check occured), returns None.
        '''
        move_color = self.move_color
        opp_move_color = get_opp_color(move_color)

        # Make move
        del self.pieces[move['position']]
        self.update_mask_remove(move['position'])
        if move['captured_piece']:
            del self.pieces[move['captured_position']]
            self.update_mask_remove(move['captured_position'])
        self.pieces[move['new_position']] = (move['new_piece'], move_color)
        self.update_mask_add(move['new_position'])

        # Castle move
        castle_info = None
        if (move['piece'] == 'king' and
                abs(move['new_position'][0] - move['position'][0]) == 2):
            r = move['position'][1]
            rook_position = (0, r) if move['new_position'][0] == 2 else (7, r)
            rook_new_position = ((move['position'][0] + move['new_position'][0]) / 2, r)

            castle_info = {
                'rook_position': rook_position,
                'rook_new_position': rook_new_position
            }
            self.pieces[rook_new_position] = self.pieces[rook_position]
            self.update_mask_add(rook_new_position)
            del self.pieces[rook_position]
            self.update_mask_remove(rook_position)

        # Move color
        self.move_color = opp_move_color
        # En passant
        old_en_passant = self.en_passant
        self.en_passant = None
        if (move['piece'] == 'pawn' and
                abs(move['new_position'][1] - move['position'][1]) == 2):
            self.en_passant = (move['position'][0], (move['new_position'][1] + move['position'][1]) / 2)
        # Castles
        old_castles = list(self.castles)
        self.castles = update_castles(
            self.castles, [move['position'], move['new_position']])

        revert_info = {
            'move': move,
            'old_en_passant': old_en_passant,
            'castle_info': castle_info,
            'old_castles': old_castles
        }

        if self.is_check():
            self.revert_move(revert_info)
            return None

        return revert_info

    def revert_move(self, revert_info):
        opp_move_color = self.move_color
        move_color = get_opp_color(opp_move_color)

        move = revert_info['move']
        castle_info = revert_info['castle_info']

        # Recover
        del self.pieces[move['new_position']]
        self.update_mask_remove(move['new_position'])
        if move['captured_piece']:
            self.pieces[move['captured_position']] = (move['captured_piece'], opp_move_color)
            self.update_mask_add(move['captured_position'])
        self.pieces[move['position']] = (move['piece'], move_color)
        self.update_mask_add(move['position'])

        # Castle move
        if castle_info is not None:
            rook_position = castle_info['rook_position']
            rook_new_position = castle_info['rook_new_position']

            self.pieces[rook_position] = self.pieces[rook_new_position]
            self.update_mask_add(rook_position)
            del self.pieces[rook_new_position]
            self.update_mask_remove(rook_new_position)

        # Revert move color
        self.move_color = move_color
        # Revert en passant
        self.en_passant = revert_info['old_en_passant']
        # Revert castles
        self.castles = revert_info['old_castles']

    def get_board_captures(self, capture_sort_key=None):
        '''
        Captures + promotions without capture
        '''
        move_color = self.move_color
        opp_move_color = get_opp_color(move_color)
        sign = color_sign(move_color)
        capture_moves = []

        for position, (piece, color) in self.pieces.items():
            if color != move_color:
                continue

            if piece == 'knight':
                for variant in PROBABLE_MOVES['knight'][position]:
                    for move in variant:
                        new_position = move['new_position']
                        new_piece = piece
                        captured_position = new_position

                        captured_piece, captured_color = self.pieces.get(captured_position, (None, None))
                        if captured_color != opp_move_color:
                            break

                        move = {
                            'position': position,
                            'new_position': new_position,
                            'piece': piece,
                            'new_piece': new_piece,
                            'captured_position': captured_position,
                            'captured_piece': captured_piece
                        }
                        capture_moves.append(move)
            else:
                promotion_pieces = [piece]
                if (piece == 'pawn' and
                        position[1] + sign in [0, 7]):
                    # Last rank
                    promotion_pieces = PROMOTION_PIECES

                    # Add promotions without capture
                    new_position = (position[0], position[1] + sign)
                    if new_position not in self.pieces:
                        for promote_piece in promotion_pieces:
                            move = {
                                'position': position,
                                'new_position': new_position,
                                'piece': piece,
                                'new_piece': promote_piece,
                                'captured_position': new_position,
                                'captured_piece': None
                            }
                            capture_moves.append(move)

                for line_type in LINE_TYPES:
                    if piece not in LINES_INFO[line_type]['pieces']:
                        continue

                    line_id, _ = CELL_TO_LINE_ID[line_type][position]
                    mask = self.masks[line_type][line_id]
                    next_cells = NEXT_CELL[position][line_type][mask]
                    en_passant_cells = ()

                    if (piece == 'pawn' and
                            self.en_passant):
                        # Extra logic for pawn
                        x = -1 if line_type == LINE_TYPE_LT else 1
                        new_position = (position[0] + x, position[1] + sign)
                        if new_position == self.en_passant:
                            en_passant_cells = (new_position, )

                    for new_position in next_cells + en_passant_cells:
                        if new_position is None:
                            continue
                        if piece == 'king':
                            # Extra logic for king
                            diff = abs(new_position[0] - position[0])
                            if diff == 0:
                                diff = abs(new_position[1] - position[1])
                            if diff > 1:
                                continue
                        elif piece == 'pawn':
                            # Extra logic for pawn
                            diff = new_position[1] - position[1]
                            if diff != sign:
                                continue

                        for new_piece in promotion_pieces:
                            captured_position = new_position
                            captured_piece, captured_color = self.pieces.get(captured_position, (None, None))
                            if not captured_piece:
                                # En passant
                                captured_position = (self.en_passant[0], self.en_passant[1] - sign)
                                captured_piece, captured_color = self.pieces[captured_position]

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
                            capture_moves.append(move)

        # capture_moves.sort(key=lambda x: (x['position'], x['new_position'], x['new_piece']))
        random.shuffle(capture_moves)

        # Sort captured moves
        if capture_sort_key is None:
            capture_sort_key = self.sort_take_by_value
        capture_moves.sort(key=capture_sort_key)

        return capture_moves

    def get_board_simple_moves(self):
        move_color = self.move_color
        opp_move_color = get_opp_color(move_color)
        sign = color_sign(move_color)

        simple_moves = []
        for position, (piece, color) in self.pieces.items():
            if color != move_color:
                continue

            new_positions = []
            if piece == 'knight':
                for variant in PROBABLE_MOVES['knight'][position]:
                    for move in variant:
                        new_position = move['new_position']

                        captured_piece, _ = self.pieces.get(new_position, (None, None))
                        if not captured_piece:
                            new_positions.append(new_position)
            elif piece == 'pawn':
                new_position = (position[0], position[1] + sign)
                if (new_position not in self.pieces
                        and new_position[1] not in [0, 7]):
                    # Do not allow promotions
                    new_positions.append(new_position)

                    if position[1] - sign in [0, 7]:
                        new_position = (position[0], position[1] + 2 * sign)
                        if new_position not in self.pieces:
                            new_positions.append(new_position)
            else:
                for line_type in LINE_TYPES:
                    if piece not in LINES_INFO[line_type]['pieces']:
                        continue

                    line_id, _ = CELL_TO_LINE_ID[line_type][position]
                    mask = self.masks[line_type][line_id]
                    new_positions.extend(FREE_MOVES[position][line_type][mask][piece])

                if piece == 'king':
                    # Castles
                    kc = self.castles[get_castle_id(move_color, 'k')]
                    qc = self.castles[get_castle_id(move_color, 'q')]
                    if (kc or
                            qc):
                        r = 0 if move_color == WHITE else 7
                        if kc:
                            assert(position == (4, r))
                            assert(self.pieces[(7, r)] == ('rook', move_color))
                        if qc:
                            assert(position == (4, r))
                            assert(self.pieces[(0, r)] == ('rook', move_color))

                        is_under_check = self.beaten_cell(position, opp_move_color)
                        if (kc and
                                not is_under_check and
                                not self.beaten_cell((position[0] + 1, r), opp_move_color)):
                            if not any((x, r) in self.pieces for x in [5, 6]):
                                new_positions.append((6, r))

                        if (qc and
                                not is_under_check and
                                not self.beaten_cell((position[0] - 1, r), opp_move_color)):
                            if not any((x, r) in self.pieces for x in [1, 2, 3]):
                                new_positions.append((2, r))

            for new_position in new_positions:
                move = {
                    'position': position,
                    'new_position': new_position,
                    'piece': piece,
                    'new_piece': piece,
                    'captured_position': new_position,
                    'captured_piece': None
                }
                simple_moves.append(move)

        # simple_moves.sort(key=lambda x: (x['position'], x['new_position'], x['new_piece']))
        random.shuffle(simple_moves)

        return simple_moves

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
        opp_move_color = get_opp_color(move_color)
        sign = color_sign(move_color)

        probable_moves = []
        if piece != 'pawn':
            probable_moves = PROBABLE_MOVES[piece][position]
        else:
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

        # Extra logic for castles
        if piece == 'king':
            # Make a copy
            probable_moves = list(probable_moves)

            # If (king, rook) haven't moved +
            # if not under check + king don't passing beaten cell +
            # if no piece is on the way
            kc = self.castles[get_castle_id(move_color, 'k')]
            qc = self.castles[get_castle_id(move_color, 'q')]
            if (kc or
                    qc):
                r = 0 if move_color == WHITE else 7
                if kc:
                    assert(position == (4, r))
                    assert(self.pieces[(7, r)] == ('rook', move_color))
                if qc:
                    assert(position == (4, r))
                    assert(self.pieces[(0, r)] == ('rook', move_color))

                is_under_check = self.beaten_cell(position, opp_move_color)
                if (kc and
                        not is_under_check and
                        not self.beaten_cell((position[0] + 1, r), opp_move_color)):
                    if not any((x, r) in self.pieces for x in [5, 6]):
                        probable_moves.append([{
                            'new_position': (6, r)
                        }])

                if (qc and
                        not is_under_check and
                        not self.beaten_cell((position[0] - 1, r), opp_move_color)):
                    if not any((x, r) in self.pieces for x in [1, 2, 3]):
                        probable_moves.append([{
                            'new_position': (2, r)
                        }])

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
            return self.beaten_cell(king_cell, check_color)

        return False

    def is_mate(self):
        '''
        Mate for self.move_color
        '''
        if not self.is_check(opposite=True):
            return False

        mate = True
        for move in self.get_board_moves():
            revert_info = self.make_move(move)
            if revert_info is None:
                continue
            self.revert_move(revert_info)

            mate = False
            break

        return mate

    def beaten_cell(self, position, by_color):
        '''
            `by_color` - color of side to beat.
        '''
        for line in BEAT_LINES[by_color][position]:
            for cell_info in line:
                piece, color = self.pieces.get(cell_info['cell'], (None, None))
                if piece:
                    if (color == by_color and
                            piece in cell_info['pieces']):
                        return True
                    break

        return False

    @staticmethod
    def sort_take_by_value(move):
        '''
        The most valueable + by the most cheap
        '''
        # Consider promotions without capture also
        # FIXME: consider promotions with capturing
        material_diff = 0
        if move['captured_piece']:
            material_diff += PIECES[move['captured_piece']]['value']
        if move['new_piece'] != move['piece']:
            material_diff += PIECES[move['new_piece']]['value']

        return [
            -material_diff, PIECES[move['piece']]['value']]

    def update_mask_add(self, position):
        for line_type in LINE_TYPES:
            line_id, cell_id = CELL_TO_LINE_ID[line_type][position]
            # ^???
            self.masks[line_type][line_id] ^= 1 << cell_id

    def update_mask_remove(self, position):
        for line_type in LINE_TYPES:
            line_id, cell_id = CELL_TO_LINE_ID[line_type][position]
            # ^???
            self.masks[line_type][line_id] ^= 1 << cell_id
