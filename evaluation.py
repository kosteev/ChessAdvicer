def material_evaluation(board):
    material = board.evaluation_params()['material']
    result = {
        'evaluation': material[0] - material[1]
    }

    return result


def simple_evaluation(board):
    result = {
        'evaluation': board.evaluation
    }

    return result
