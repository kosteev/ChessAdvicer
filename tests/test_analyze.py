import unittest
from nose.tools import assert_equal

from analyze import SimpleAnalyzer, AlphaAnalyzer, AlphaBetaAnalyzer
from evaluation import simple_evaluation
from mocks import get_mock
from utils import print_board


analyzer_classes = [SimpleAnalyzer, AlphaAnalyzer, AlphaBetaAnalyzer]


class TestAnalyzer(unittest.TestCase):
    def test_mock_0_deep_1(self):
        lines = 5
        for analyzer_class in analyzer_classes:
            analyzer = analyzer_class(
                max_deep=1, evaluation_func=simple_evaluation, lines=lines)
            board = get_mock(0)
    
            analysis = analyzer.analyze(board)
            result = analysis['result']
    
            to_check = []
            for ind in xrange(3):
                to_check.append(
                    (result[ind]['evaluation'], result[ind]['moves'][-1]['piece'], result[ind]['moves'][-1]['new_position']))
    
            to_check.sort()
            assert_equal(to_check[0], (-2, 'pawn', (0, 1)))
            assert_equal(to_check[1], (-2, 'rook', (0, 1)))
            assert_equal(to_check[2][0], -1)
            assert_equal(len(result), lines)

    def test_mock_0_deep_2(self):
        lines = 10
        for analyzer_class in analyzer_classes:
            analyzer = analyzer_class(
                max_deep=2, evaluation_func=simple_evaluation, lines=lines)
            board = get_mock(0)
    
            analysis = analyzer.analyze(board)
            result = analysis['result']
    
            to_check = []
            for ind in xrange(8):
                to_check.append(
                    (result[ind]['evaluation'], result[ind]['moves'][-1]['piece'], result[ind]['moves'][-1]['new_position']))
    
            to_check.sort()
            assert_equal(to_check[0], (-1, 'king', (3, 0)))
            assert_equal(to_check[1], (-1, 'king', (3, 1)))
            assert_equal(to_check[2], (-1, 'pawn', (0, 1)))
            assert_equal(to_check[3], (-1, 'rook', (0, 3)))
            assert_equal(to_check[4], (-1, 'rook', (0, 4)))
            assert_equal(to_check[5], (-1, 'rook', (0, 5)))
            assert_equal(to_check[6], (-1, 'rook', (0, 6)))
            assert_equal(to_check[7][0], 0)
            assert_equal(len(result), lines)

    def test_mock_0_deep_3(self):
        lines = 17
        for analyzer_class in analyzer_classes:
            analyzer = analyzer_class(
                max_deep=3, evaluation_func=simple_evaluation, lines=lines)
            board = get_mock(0)
    
            analysis = analyzer.analyze(board)
            result = analysis['result']
    
            to_check = []
            for ind in xrange(9):
                to_check.append(
                    (result[ind]['evaluation'], result[ind]['moves'][-1]['piece'], result[ind]['moves'][-1]['new_position']))
    
            to_check.sort()
            assert_equal(to_check[0], (-2, 'king', (3, 0)))
            assert_equal(to_check[1], (-2, 'king', (3, 1)))
            assert_equal(to_check[2], (-2, 'pawn', (0, 1)))
            assert_equal(to_check[3], (-2, 'rook', (0, 3)))
            assert_equal(to_check[4], (-2, 'rook', (0, 4)))
            assert_equal(to_check[5], (-2, 'rook', (0, 5)))
            assert_equal(to_check[6], (-2, 'rook', (0, 6)))
            assert_equal(to_check[7], (-1, 'rook', (1, 7)))
            assert_equal(to_check[8][0], 0)
            assert_equal(len(result), 16)

    def test_mock_2_deep_4(self):
        lines = 17
        for analyzer_class in analyzer_classes:
            analyzer = analyzer_class(
                max_deep=4, evaluation_func=simple_evaluation, lines=lines)
            board = get_mock(2)
    
            analysis = analyzer.analyze(board)
            result = analysis['result']
    
            to_check = []
            for ind in xrange(9):
                to_check.append(
                    (result[ind]['evaluation'], result[ind]['moves'][-1]['piece'], result[ind]['moves'][-1]['new_position']))
    
            to_check.sort(reverse=True)
            assert_equal(to_check[0], (997, 'queen', (6, 7)))
            assert_equal(to_check[1][0], 5)
            assert_equal(len(result), 17)