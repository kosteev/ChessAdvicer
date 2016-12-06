import json
import urllib
import urllib2

from board import Board
from pieces import WHITE, PIECES
from utils import name_to_cell, color_sign


def get_syzygy_best_move(board):
    '''
    WDL - 6 pieces
    DTM - 5 pieces
    '''
    if len(board.pieces) > 6:
        return None

    fen = generate_fen(board)
    try:
        response = urllib2.urlopen(
            "https://syzygy-tables.info/api/v2?fen={}".format(urllib.quote(fen))).read()
        parsed = json.loads(response)
    except Exception:
        return None

    parsed_moves = [{
        'key': key,
        'wdl': value['wdl'],
        'dtm': value['dtm']
    } for key, value in parsed['moves'].items()]

    if not parsed_moves:
        # Is it a draw?
        return None

    if len(board.pieces) == 6:
        parsed_moves.sort(key=lambda x: x['wdl'])
    else:
        parsed_moves.sort(key=lambda x: (x['wdl'], -x['dtm']))

    parsed_move = parsed_moves[0]

    # TODO: promotions
    sign = color_sign(board.move_color)
    if parsed_move['wdl'] == 0:
        evaluation = 0
    else:
        if parsed_move['dtm'] is None:
            evaluation = Board.MAX_EVALUATION
        else:
            evaluation = Board.MAX_EVALUATION - abs(parsed_move['dtm']) - 1
        if parsed_move['wdl'] > 0:
            evaluation *= -1
        evaluation *= sign

    position = name_to_cell(parsed_move['key'][:2])
    new_position = name_to_cell(parsed_move['key'][2:4])
    piece = board.pieces[position][0]
    new_position_old_piece = board.pieces.get(new_position)

    move = {
        'position': position,
        'new_position': new_position,
        'piece': piece,
        'new_piece': piece,
        'new_position_old_piece': new_position_old_piece
    }
    
    return {
        'evaluation': evaluation,
        'moves': [move]
    }


def generate_fen(board):
    fen_1 = []
    for r in xrange(7, -1, -1):
        row = ""
        empty = 0
        for c in xrange(8):
            cell = (c, r)
            
            if cell in board.pieces:
                if empty:
                    row += str(empty)

                piece, color = board.pieces[cell]
                title = PIECES[piece]['title']
                if color == WHITE:
                    title = title.upper()
                else:
                    title = title.lower()

                row += title
                empty = 0
            else:
                empty += 1
        if empty:
            row += str(empty)

        fen_1.append(row)

    # TODO: provide k/q castles
    # TODO: provide on passan
    fen = "{} {} - - 0 1".format("/".join(fen_1), "w" if board.move_color == WHITE else "b")
    return fen
