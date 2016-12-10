import json
import random
import urllib
import urllib2

from board import Board
from pieces import get_piece_by_title
from utils import name_to_cell, color_sign, get_fen_from_board


def get_syzygy_best_move(board):
    '''
    WDL - 6 pieces
    DTM - 5 pieces
    '''
    if len(board.pieces) > 6:
        return None

    fen = get_fen_from_board(board)
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

    random.shuffle(parsed_moves)
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
            evaluation = Board.MAX_EVALUATION / 2
        else:
            evaluation = Board.MAX_EVALUATION / 2 - abs(parsed_move['dtm']) - 1
        if parsed_move['wdl'] > 0:
            evaluation *= -1
        evaluation *= sign

    position = name_to_cell(parsed_move['key'][:2])
    new_position = name_to_cell(parsed_move['key'][2:4])
    piece = board.pieces[position][0]
    new_piece = piece
    if len(parsed_move['key']) == 5:
        new_piece = get_piece_by_title(parsed_move['key'][4])
    new_position_old_piece = board.pieces.get(new_position)

    move = {
        'position': position,
        'new_position': new_position,
        'piece': piece,
        'new_piece': new_piece,
        'new_position_old_piece': new_position_old_piece
    }
    
    return {
        'evaluation': evaluation,
        'moves': [move]
    }
