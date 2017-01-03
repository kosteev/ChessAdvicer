def material_evaluation(board):
    result = {
        'evaluation': board.material[0] - board.material[1]
    }

    return result


def simple_evaluation(board):
    result = {
        'evaluation': board.evaluation
    }

    return result
