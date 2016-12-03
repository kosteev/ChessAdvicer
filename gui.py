import pyautogui


from board_detection import CELL_SIZE


def focus_board(board):
    x = board.lt_screen[0]
    y = board.lt_screen[1] - 5

    pyautogui.click(x, y)


def click_cell(board, position):
    x = board.lt_screen[0] + (position[0] + 0.5) * CELL_SIZE / 2
    y = board.lt_screen[1] + (position[1] + 0.5) * CELL_SIZE / 2

    pyautogui.click(x, y)


def make_move(board, position, new_position):
    focus_board(board)
    click_cell(board, position)
    click_cell(board, new_position)
