from board import Board
from pieces import WHITE, BLACK


MOCKS_COUNT = 3


def get_mock(mock_id):
    if mock_id == 0:
        # Checkmate in two moves
        pieces = {
            (0, 0): ('king', WHITE),
            (1, 0): ('bishop', WHITE),
            (0, 1): ('pawn', WHITE),
            (1, 1): ('pawn', WHITE),
            (2, 0): ('king', BLACK),
            (1, 2): ('pawn', BLACK),
            (0, 7): ('rook', BLACK),
        }
        
        return Board(
            pieces=pieces,
            move_up_color=BLACK,
            move_color=BLACK
        )

    if mock_id == 1:
        # Initial position
        pieces = {}
        for c in xrange(8):
            pieces[(c, 1)] = ('pawn', BLACK)
            pieces[(c, 6)] = ('pawn', WHITE)
        for r in [0, 7]:
            color = BLACK if r == 0 else WHITE
            pieces[(0, r)] = ('rook', color)
            pieces[(7, r)] = ('rook', color)
            pieces[(1, r)] = ('knight', color)
            pieces[(6, r)] = ('knight', color)
            pieces[(2, r)] = ('bishop', color)
            pieces[(5, r)] = ('bishop', color)
            pieces[(3, r)] = ('queen', color)
            pieces[(4, r)] = ('king', color)

        return Board(
            pieces=pieces,
            move_up_color=WHITE,
            move_color=WHITE
        )

    if mock_id == 2:
        # Initial position
        pieces = {}
        pieces[(7, 0)] = ('king', BLACK)
        pieces[(5, 0)] = ('rook', BLACK)
        pieces[(7, 1)] = ('pawn', BLACK)
        pieces[(6, 1)] = ('pawn', BLACK)
        pieces[(7, 2)] = ('knight', WHITE)
        pieces[(3, 3)] = ('queen', WHITE)
        pieces[(7, 7)] = ('king', WHITE)

        return Board(
            pieces=pieces,
            move_up_color=WHITE,
            move_color=WHITE
        )
