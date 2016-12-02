from board import Board


def get_mock(mock_id):
    if mock_id == 0:
        # Checkmate in two moves
        pieces = {
            (0, 0): ('king', 'white'),
            (1, 0): ('bishop', 'white'),
            (0, 1): ('pawn', 'white'),
            (1, 1): ('pawn', 'white'),
            (2, 0): ('king', 'black'),
            (1, 2): ('pawn', 'black'),
            (0, 7): ('rook', 'black'),
        }
        
        return Board(
            pieces=pieces,
            move_up_color='black',
            move_color='black',
            xy=None
        )

    if mock_id == 1:
        # Initial position
        pieces = {}
        for c in xrange(8):
            pieces[(c, 1)] = ('pawn', 'black')
            pieces[(c, 6)] = ('pawn', 'white')
        for r in [0, 7]:
            pieces[(0, r)] = ('rook', 'black' if r == 0 else 'white')
            pieces[(7, r)] = ('rook', 'black' if r == 0 else 'white')
            pieces[(1, r)] = ('knight', 'black' if r == 0 else 'white')
            pieces[(6, r)] = ('knight', 'black' if r == 0 else 'white')
            pieces[(2, r)] = ('bishop', 'black' if r == 0 else 'white')
            pieces[(5, r)] = ('bishop', 'black' if r == 0 else 'white')
            pieces[(3, r)] = ('queen', 'black' if r == 0 else 'white')
            pieces[(4, r)] = ('king', 'black' if r == 0 else 'white')

        return Board(
            pieces=pieces,
            move_up_color='black',
            move_color='black',
            xy=None
        )

    if mock_id == 2:
        # Initial position
        pieces = {}
        for c in xrange(8):
            pieces[(c, 1)] = ('pawn', 'black')
            pieces[(c, 6)] = ('pawn', 'white')
        for r in [0, 7]:
            pieces[(0, r)] = ('rook', 'black' if r == 0 else 'white')
            pieces[(7, r)] = ('rook', 'black' if r == 0 else 'white')
            pieces[(1, r)] = ('knight', 'black' if r == 0 else 'white')
            pieces[(6, r)] = ('knight', 'black' if r == 0 else 'white')
            pieces[(2, r)] = ('bishop', 'black' if r == 0 else 'white')
            pieces[(5, r)] = ('bishop', 'black' if r == 0 else 'white')
            pieces[(3, r)] = ('queen', 'black' if r == 0 else 'white')
            pieces[(4, r)] = ('king', 'black' if r == 0 else 'white')

        return Board(
            pieces=pieces,
            move_up_color='black',
            move_color='black',
            xy=None
        )
