import pyautogui


from board_detection import CELL_SIZE


def focus_board(board):
    x = board.xy[0]
    y = board.xy[1] - 10

    pyautogui.click(x / 2, y / 2)


def click_cell(board, position):
    x = board.xy[0] + (position[0] + 0.5) * CELL_SIZE
    y = board.xy[1] + (position[1] + 0.5) * CELL_SIZE

    pyautogui.click(x / 2, y / 2)


def make_move(board, position, new_position):
    original_position = pyautogui.position()

    focus_board(board)
    click_cell(board, position)
    click_cell(board, new_position)

    pyautogui.moveTo(original_position)
    