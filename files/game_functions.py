# game_functions.py
# This module implements the core game mechanics for 2048, including tile movement and merging.

import numpy as np
from numba import njit

CELL_COUNT = 4  # Number of tiles in a row/column
NUMBER_OF_SQUARES = CELL_COUNT * CELL_COUNT  # Total number of tiles on the board
NEW_TILE_DISTRIBUTION = np.array([2] * 9 + [4])  # 90% chance for 2, 10% for 4

@njit
def initialize_game():
    """
    Initializes the game board with two randomly placed tiles of value 2.
    Returns:
        numpy.ndarray: The initialized game board.
    """
    board = np.zeros((CELL_COUNT, CELL_COUNT), dtype=np.int32)
    initial_twos = np.random.choice(NUMBER_OF_SQUARES, 2, replace=False)
    for pos in initial_twos:
        row, col = divmod(pos, CELL_COUNT)
        board[row][col] = 2
    return board

@njit
def add_new_tile(board):
    """
    Adds a new tile (2 or 4) to a random empty cell on the board.
    Parameters:
        board (numpy.ndarray): The current game board.
    Returns:
        numpy.ndarray: The updated game board with the new tile.
    """
    tile_value = np.random.choice(NEW_TILE_DISTRIBUTION)
    empty_cells = list(zip(*np.where(board == 0)))
    if not empty_cells:
        return board  # No empty cells, no new tile added
    row, col = empty_cells[np.random.randint(len(empty_cells))]
    board[row][col] = tile_value
    return board

@njit
def push_board_right(board):
    """
    Slides all tiles to the right without merging.
    Parameters:
        board (numpy.ndarray): The current game board.
    Returns:
        tuple: The updated board and a boolean indicating if any tiles moved.
    """
    new = np.zeros_like(board)
    done = False
    for row in range(CELL_COUNT):
        count = CELL_COUNT - 1
        for col in range(CELL_COUNT - 1, -1, -1):
            if board[row][col] != 0:
                new[row][count] = board[row][col]
                if col != count:
                    done = True
                count -= 1
    return new, done

@njit
def merge_elements(board):
    """
    Merges adjacent tiles of the same value and doubles their value.
    Parameters:
        board (numpy.ndarray): The current game board.
    Returns:
        tuple: The updated board, a boolean indicating if any tiles merged, and the score increment.
    """
    score = 0
    done = False
    for row in range(CELL_COUNT):
        for col in range(CELL_COUNT - 1, 0, -1):
            if board[row][col] == board[row][col - 1] and board[row][col] != 0:
                board[row][col] *= 2
                score += board[row][col]
                board[row][col - 1] = 0
                done = True
    return board, done, score

@njit
def move_up(board):
    """
    Moves all tiles up and merges adjacent tiles if possible.
    Parameters:
        board (numpy.ndarray): The current game board.
    Returns:
        tuple: The updated board, a boolean indicating if any move was made, and the score increment.
    """
    rotated_board = np.rot90(board, -1)
    pushed_board, has_pushed = push_board_right(rotated_board)
    merged_board, has_merged, score = merge_elements(pushed_board)
    second_pushed_board, _ = push_board_right(merged_board)
    rotated_back_board = np.rot90(second_pushed_board)
    move_made = has_pushed or has_merged
    return rotated_back_board, move_made, score

@njit
def move_down(board):
    """
    Moves all tiles down and merges adjacent tiles if possible.
    Parameters:
        board (numpy.ndarray): The current game board.
    Returns:
        tuple: The updated board, a boolean indicating if any move was made, and the score increment.
    """
    rotated_board = np.rot90(board)
    pushed_board, has_pushed = push_board_right(rotated_board)
    merged_board, has_merged, score = merge_elements(pushed_board)
    second_pushed_board, _ = push_board_right(merged_board)
    rotated_back_board = np.rot90(second_pushed_board, -1)
    move_made = has_pushed or has_merged
    return rotated_back_board, move_made, score

@njit
def move_left(board):
    """
    Moves all tiles left and merges adjacent tiles if possible.
    Parameters:
        board (numpy.ndarray): The current game board.
    Returns:
        tuple: The updated board, a boolean indicating if any move was made, and the score increment.
    """
    rotated_board = np.rot90(board, 2)
    pushed_board, has_pushed = push_board_right(rotated_board)
    merged_board, has_merged, score = merge_elements(pushed_board)
    second_pushed_board, _ = push_board_right(merged_board)
    rotated_back_board = np.rot90(second_pushed_board, -2)
    move_made = has_pushed or has_merged
    return rotated_back_board, move_made, score

@njit
def move_right(board):
    """
    Moves all tiles right and merges adjacent tiles if possible.
    Parameters:
        board (numpy.ndarray): The current game board.
    Returns:
        tuple: The updated board, a boolean indicating if any move was made, and the score increment.
    """
    pushed_board, has_pushed = push_board_right(board)
    merged_board, has_merged, score = merge_elements(pushed_board)
    second_pushed_board, _ = push_board_right(merged_board)
    move_made = has_pushed or has_merged
    return second_pushed_board, move_made, score

@njit
def check_game_over(board):
    """
    Checks if no valid moves are possible.
    Parameters:
        board (numpy.ndarray): The current game board.
    Returns:
        bool: True if no moves are possible, False otherwise.
    """
    # Test all moves
    _, move_made, _ = move_up(board)
    if move_made:
        return False
    _, move_made, _ = move_down(board)
    if move_made:
        return False
    _, move_made, _ = move_left(board)
    if move_made:
        return False
    _, move_made, _ = move_right(board)
    if move_made:
        return False
    return True  # No moves possible