from utils import get_board_from_fen


FENS = {
    0: 'r7/8/8/8/8/1p6/PP6/KBk5 b - - - -',
    1: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - - -',  # Initial position
    2: '5r1k/6pp/7N/3Q4/8/8/8/7K w - - - -',
    3: '4k2N/5nRB/6P1/2rQ1K2/8/8/8/8 w - - - -',
    4: '2k5/8/4P3/3K4/8/8/8/8 w - - - -',
    5: '8/5P1k/5K2/8/8/8/8/8 w - - - -',
    6: '8/8/2k5/4b3/5p2/4pP1P/4P1PK/4n1NR w - - - -',
    7: '8/8/2k5/4b3/5pP1/4pP1P/4P2K/4n1NR b - g3 - -',
    8: '8/8/8/8/8/8/5R2/1k2K2R w K - - -',  # Mate in one with O-O
    9: 'rnbqkb1r/pppppp1p/5np1/8/8/4PN2/PPPP1PPP/RNBQKB1R w KQkq - - -',
    10: 'rnbqkb1r/pppp1p1p/4pnp1/8/8/4PN2/PPPPBPPP/RNBQK2R w KQkq - - -',
    11: 'rnbqk2r/pppp1p1p/4pnpb/8/8/BP2PN2/P1PPBPPP/RN1QK2R b KQkq - - -',
    12: 'rn4r1/ppp1qpkp/3p1npb/4p1N1/3PP1b1/BPNQ4/P1P2PPP/R3KBR1 w Q - - -',
    13: 'rn4r1/ppp1qpkp/3p1np1/4p3/3PP1bb/BPNQ1P2/P1P3PP/R3KB1R w Q - - -',
    14: 'rnbqkb1r/pppp1p1p/4pnp1/8/8/4PN2/PPPPBPPP/RNBQK2R w Qkq - - -',
    15: '8/8/8/8/8/5P2/4QP2/k3K1NR w K - - -',
    16: 'r3k3/8/8/1B6/8/8/8/8 b q - - -',
    17: 'r1bq1rk1/pp3pbp/3p1np1/2pN4/3pP3/3B4/PPPPQPPP/R1B2RK1 w - c6 - -',
    18: '5rnn/4P1pk/3K2pp/8/8/8/8/8 w - - - -',
    19: '4k2r/1Pb1pppp/n3n2n/8/n2p1Q1Q/8/4P2n/R3K3 b Qk - - -',
    20: '7k/8/8/3p4/1n6/8/2R1P3/7K w - - - -',
    21: '6nn/5Ppk/3K2pp/8/8/8/8/8 w - - - -',
    22: '2r1n2k/1P3P2/8/8/8/8/8/7K w - - - -'
}
MOCKS_COUNT = len(FENS)


def get_mock(mock_id):
    return get_board_from_fen(FENS[mock_id])
