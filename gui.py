import pyautogui


from utils import normalize_cell


def focus_board(board):
    x = board.lt_screen[0] - 1
    y = board.lt_screen[1] - 1

    pyautogui.click(x, y)


def click_cell(board, position):
    position = normalize_cell(position, board.move_up_color)
    x = board.lt_screen[0] + (position[0] + 0.5) * board.cell_size
    y = board.lt_screen[1] + (7 - position[1] + 0.5) * board.cell_size

    pyautogui.click(x, y)


def make_move(board, position, new_position):
    focus_board(board)
    click_cell(board, position)
    click_cell(board, new_position)
