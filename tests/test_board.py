import unittest
from nose.tools import assert_equal, assert_true

from board import Board
from mocks import MOCKS_COUNT, get_mock
from pieces import WHITE, BLACK, WHITE_KC, WHITE_QC, BLACK_QC, get_castles
from utils import print_board


class Test(unittest.TestCase):
    def test_hash(self):
        hashes = set()
        for mock_id in xrange(MOCKS_COUNT):
            hashes.add(get_mock(mock_id).hash)

        assert_equal(len(hashes), MOCKS_COUNT)

        pieces = {
            (0, 0): ('king', WHITE),
            (7, 6): ('king', BLACK)
        }

        hashes = set()
        hashes.add(Board(pieces, move_color=WHITE).hash)
        hashes.add(Board(pieces, move_color=BLACK).hash)
        hashes.add(Board(pieces, move_color=BLACK, en_passant=(2, 2)).hash)
        hashes.add(Board(pieces, move_color=BLACK, castles=get_castles(white_qc=True, black_kc=True)).hash)
        hashes.add(Board(pieces, move_color=BLACK, castles=get_castles(white_kc=True)).hash)
        hashes.add(Board(pieces, move_color=BLACK, castles=get_castles(black_qc=True)).hash)

        assert_equal(len(hashes), 6)

    def test_complex(self):
        board = get_mock(3)
        print_board(board)

        d = [{
            'move': {
                'position': (3, 4),
                'new_position': (2, 4),
                'piece': 'queen',
                'new_piece': 'queen',
                'captured_piece': 'rook',
                'captured_position': (2, 4)
            },
            'evaluation': 18,
            'positional_eval': 44
        }, {
            'move': {
                'position': (6, 5),
                'new_position': (5, 6),
                'piece': 'pawn',
                'new_piece': 'pawn',
                'captured_piece': 'knight',
                'captured_position': (5, 6)
            },
            'evaluation': 16,
            'positional_eval': 38
        }, {
            'move': {
                'position': (7, 7),
                'new_position': (5, 6),
                'piece': 'knight',
                'new_piece': 'knight',
                'captured_piece': 'knight',
                'captured_position': (5, 6)
            },
            'evaluation': 16,
            'positional_eval': 42
        }, {
            'move': {
                'position': (6, 6),
                'new_position': (5, 6),
                'piece': 'rook',
                'new_piece': 'rook',
                'captured_piece': 'knight',
                'captured_position': (5, 6)
            },
            'evaluation': 16,
            'positional_eval': 38
        }]

        cnt = 0
        assert_equal(board.material, 13)
        for move in board.get_board_moves(capture_sort_key=Board.sort_take_by_value):
            revert_info = board.make_move(move)
            if revert_info is None:
                continue

            if cnt < len(d):
                assert_equal(move, d[cnt]['move'])
                assert_equal(board.material, d[cnt]['evaluation'])
                assert_equal(board.positional_eval, d[cnt]['positional_eval'])
            else:
                assert_equal(board.material, 13)
            cnt += 1

            board.revert_move(revert_info)

    def test_en_passant(self):
        board = get_mock(7)
        print_board(board)

        assert_equal(board.en_passant, (6, 2))
        assert_equal(board.material, 4)
        assert_equal(board.positional_eval, 3)
        assert_true(board.pieces[(6, 3)] == ('pawn', WHITE))
        cnt = 0
        for move in board.get_board_moves(capture_sort_key=Board.sort_take_by_value):
            revert_info = board.make_move(move)
            if revert_info is None:
                continue

            if cnt == 0:
                assert_equal(move['piece'], 'pawn')
                assert_equal(move['new_position'], (6, 2))
                assert_equal(move['captured_piece'], 'pawn')
                assert_equal(board.material, 3)
                assert_equal(board.positional_eval, 1)
                assert_true((6, 3) not in board.pieces)
            cnt += 1

            board.revert_move(revert_info)

        assert_true(board.pieces[(6, 3)] == ('pawn', WHITE))

    def test_castle_obstacle_not_valid(self):
        for mock_id in [1, 9, 14]:
            board = get_mock(mock_id)
            print_board(board)

            for move in board.get_board_moves():
                revert_info = board.make_move(move)
                if revert_info is None:
                    continue

                board.revert_move(revert_info)

                if (move['piece'] == 'king' and
                        move['new_position'] == (6, 0)):
                    assert_true(False)

    def test_castle_valid(self):
        for mock_id in [10]:
            board = get_mock(mock_id)
            print_board(board)

            assert_equal(board.castles[WHITE_KC], True)
            assert_equal(board.castles[WHITE_QC], True)
            for move in board.get_board_moves():
                revert_info = board.make_move(move)
                if revert_info is None:
                    continue

                if (move['piece'] == 'king' and
                    move['new_position'] == (6, 0) and
                    (4, 0) not in board.pieces and
                    board.pieces[(5, 0)] == ('rook', WHITE) and
                    board.pieces[(6, 0)] == ('king', WHITE) and
                        (7, 0) not in board.pieces):
                    break

                board.revert_move(revert_info)
            else:
                assert_true(False)

    def test_castle_beaten_cell_check(self):
        for mock_id in [11, 12, 13]:
            board = get_mock(mock_id)
            print_board(board)

            for move in board.get_board_moves():
                revert_info = board.make_move(move)
                if revert_info is None:
                    continue

                board.revert_move(revert_info)

                if (move['piece'] == 'king' and
                        abs(move['new_position'][0] - move['position'][0]) == 2):
                    assert_true(False)

    def test_castle_become_invalid(self):
        for mock_id in [16]:
            board = get_mock(mock_id)
            print_board(board)

            assert_equal(board.castles[BLACK_QC], True)
            is_any_move = False
            for move in board.get_board_moves():
                revert_info = board.make_move(move)
                if revert_info is None:
                    continue

                assert_equal(board.castles[BLACK_QC], False)
                board.revert_move(revert_info)
                is_any_move = True

            assert_equal(is_any_move, True)
            assert_equal(board.castles[BLACK_QC], True)

    def test_copy(self):
        for mock_id in xrange(MOCKS_COUNT):
            board = get_mock(mock_id)
            board2 = board.copy()

            assert_equal(board.hash, board2.hash)

    def test_get_board_moves(self):
        l1 = []
        for mock_id in xrange(MOCKS_COUNT):
            board = get_mock(mock_id)
            l1.append(sorted(board.get_board_moves()))

        l2 = []
        for mock_id in xrange(MOCKS_COUNT):
            board = get_mock(mock_id)
            l2.append(sorted(board.get_board_moves()))

        assert_equal(l1, l2)