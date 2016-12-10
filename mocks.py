from utils import get_board_from_fen


FENS = {
    0: 'r7/8/8/8/8/1p6/PP6/KBk5 b - - - -',
    1: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - - -',
    2: '5r1k/6pp/7N/3Q4/8/8/8/7K w - - - -',
    3: '4k2N/5nRB/6P1/2rQ1K2/8/8/8/8 w - - - -',
    4: '2k5/8/4P3/3K4/8/8/8/8 w - - - -',
    5: '8/5P1k/5K2/8/8/8/8/8 w - - - -'
}
MOCKS_COUNT = len(FENS)


def get_mock(mock_id):
    return get_board_from_fen(FENS[mock_id])
