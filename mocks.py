from utils import get_board_from_fen


MOCKS_COUNT = 3


def get_mock(mock_id):
    if mock_id == 0:
        fen = 'r7/8/8/8/8/1p6/PP6/KBk5 b - - - -'
    elif mock_id == 1:
        # Initial position
        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - - -'
    elif mock_id == 2:
        fen = '5r1k/6pp/7N/3Q4/8/8/8/7K w - - - -'

    return get_board_from_fen(fen)
