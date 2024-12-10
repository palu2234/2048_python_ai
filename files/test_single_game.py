# test_single_game.py

import numpy as np
import game_ai
import game_functions as gf

def get_tile_frequencies_from_score(score_increment, tile_values=[16384, 8192, 4096, 2048, 1024]):
    freq = {tile: 0 for tile in tile_values}
    remaining = score_increment
    for tile in tile_values:
        while remaining >= tile:
            freq[tile] += 1
            remaining -= tile
    return freq

def play_single_game(ai_move_func):
    board = gf.initialize_game()
    score = 0
    highest_tile = 0
    moves = 0
    tile_frequency = {1024: 0, 2048: 0, 4096: 0, 8192: 0, 16384: 0}
    moves_until_2048_found = None

    while True:
        new_board, move_made, score_increment = ai_move_func(board.copy())

        if not move_made:
            print("No move made. Game Over.")
            break

        score += score_increment
        current_highest_tile = np.max(new_board)
        highest_tile = max(highest_tile, current_highest_tile)
        moves += 1

        if highest_tile >= 2048 and moves_until_2048_found is None:
            moves_until_2048_found = moves
            print(f"2048 tile achieved at move {moves_until_2048_found}")

        merged_tile_freq = get_tile_frequencies_from_score(score_increment)
        for tile, count in merged_tile_freq.items():
            tile_frequency[tile] += count

        board = gf.add_new_tile(new_board)

        print(f"Move {moves}:")
        print(board)
        print(f"Score: {score}, Highest Tile: {highest_tile}\n")

        if gf.check_game_over(board):
            print("Game Over after checking game over condition.")
            break

    win = highest_tile >= 2048

    print(f"Final Score: {score}")
    print(f"Highest Tile: {highest_tile}")
    print(f"Total Moves: {moves}")
    print(f"Win: {win}")
    print(f"Tile Frequencies: {tile_frequency}")

if __name__ == "__main__":
    play_single_game(game_ai.ai_move)
