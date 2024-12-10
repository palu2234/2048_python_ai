# game_ai.py

import numpy as np
import math
from numba import njit
from game_functions import move_up, move_down, move_left, move_right, check_game_over

CELL_COUNT = 4
SEARCH_DEPTH = 5

# Heuristic weights for evaluating board states
SCORE_LOST_PENALTY = 20000.0
SCORE_MONOTONICITY_WEIGHT = 4
SCORE_EMPTY_WEIGHT = 27.0
SCORE_MERGES_WEIGHT = 70.0

def calculate_fullness(board):
    """
    Calculates the fullness of the board.

    Args:
        board (np.ndarray): The current game board.

    Returns:
        float: Fullness percentage (0 to 1).
    """
    filled_cells = np.sum(board != 0)
    total_cells = board.size
    return filled_cells / total_cells

def ai_move(board, default_depth=SEARCH_DEPTH):
    """
    Determines the best move using the Expectimax algorithm with dynamic search depth based on board fullness.

    Args:
        board (np.ndarray): The current game board.
        default_depth (int): The default search depth when the board is less than 50% full.

    Returns:
        tuple: (new_board, move_made, score_increment)
    """
    # Calculate board fullness
    fullness = calculate_fullness(board)

    # Determine dynamic search depth
    if fullness >= 1:
        current_depth = default_depth + 5  # Depth 7
    elif fullness >= 0.85:
        current_depth = default_depth + 2  # Depth 7
    elif fullness >= 0.6:
        current_depth = default_depth      # Depth 5
    elif fullness >= 0.5:
        current_depth = default_depth - 2  # Depth 3
    elif fullness >= 0.4:
        current_depth = default_depth - 3  # Depth 2
    else:
        current_depth = default_depth - 4  # Depth 1

    # Optional: Print the current search depth for debugging
    # print(f"Board Fullness: {fullness*100:.2f}%, Search Depth: {current_depth}")

    # Run the Expectimax algorithm with the determined depth
    move_tuple, score = expectimax(board, depth=0, is_player=True, max_depth=current_depth)
    if move_tuple is not None:
        move_func, _ = move_tuple
        new_board, move_made, score_increment = move_func(board.copy())
        return new_board, move_made, score_increment
    else:
        return board, False, 0

def expectimax(board, depth, is_player, max_depth):
    """
    Expectimax algorithm implementation.

    Args:
        board (np.ndarray): The current game board.
        depth (int): Current depth in the search tree.
        is_player (bool): True if the current turn is the player's.
        max_depth (int): The maximum depth for the search.

    Returns:
        tuple: (best_move_tuple, best_score)
    """
    if depth >= max_depth or check_game_over(board):
        return (None, evaluate(board)), evaluate(board)

    if is_player:
        best_score = -math.inf
        best_move = None

        # Explicitly try all four moves
        for move_func in [move_up, move_down, move_left, move_right]:
            new_board, move_made, score_increment = move_func(board.copy())
            if not move_made:
                continue
            _, recursive_score = expectimax(new_board, depth + 1, False, max_depth)
            total_score = score_increment + recursive_score
            if total_score > best_score:
                best_score = total_score
                best_move = (move_func, score_increment)
        return (best_move, best_score)
    else:
        # Chance node logic
        empty_cells = list(zip(*np.where(board == 0)))
        if not empty_cells:
            return (None, evaluate(board)), evaluate(board)
        total_score = 0
        probability_per_cell = 1 / len(empty_cells)
        for cell in empty_cells:
            for value, prob in [(2, 0.9), (4, 0.1)]:
                new_board = board.copy()
                new_board[cell] = value
                _, recursive_score = expectimax(new_board, depth + 1, True, max_depth)
                total_score += prob * probability_per_cell * recursive_score
        return (None, total_score), total_score

@njit
def evaluate(board):
    """
    Evaluates the board using the defined heuristics.

    Args:
        board (np.ndarray): The current game board.

    Returns:
        float: The heuristic score of the board.
    """
    return (
        SCORE_EMPTY_WEIGHT * count_empty(board) +
        SCORE_MERGES_WEIGHT * count_merges(board) -
        SCORE_MONOTONICITY_WEIGHT * monotonicity(board)
    )

@njit
def count_empty(board):
    """
    Counts the number of empty cells on the board.

    Args:
        board (np.ndarray): The current game board.

    Returns:
        int: Number of empty cells.
    """
    return np.sum(board == 0)

@njit
def count_merges(board):
    """
    Counts the number of possible merges on the board.

    Args:
        board (np.ndarray): The current game board.

    Returns:
        int: Number of possible merges.
    """
    merges = 0
    for row in board:
        for i in range(len(row) - 1):
            if row[i] == row[i + 1] and row[i] != 0:
                merges += 1
    for col in board.T:
        for i in range(len(col) - 1):
            if col[i] == col[i + 1] and col[i] != 0:
                merges += 1
    return merges

@njit
def monotonicity(board):
    """
    Calculates the monotonicity of the board.

    Args:
        board (np.ndarray): The current game board.

    Returns:
        float: Monotonicity score.
    """
    totals = np.zeros(4)
    for row in board:
        for i in range(len(row) - 1):
            if row[i] > row[i + 1]:
                totals[0] += row[i] - row[i + 1]
            elif row[i] < row[i + 1]:
                totals[1] += row[i + 1] - row[i]
    for col in board.T:
        for i in range(len(col) - 1):
            if col[i] > col[i + 1]:
                totals[2] += col[i] - col[i + 1]
            elif col[i] < col[i + 1]:
                totals[3] += col[i + 1] - col[i]
    return min(totals[0], totals[1]) + min(totals[2], totals[3])