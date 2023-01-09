import random

import chess
import chess.engine

from database.util import board_to_obs, stockfish_evaluate, DataSet, DIRECTORY, save_dataset


# This file is used to create random board positions

# Create a random board by just playing random moves
def random_board(max_depth=400):
    board = chess.Board()
    depth = random.randrange(0, max_depth)
    for _ in range(depth):
        all_moves = list(board.legal_moves)
        random_move = random.choice(all_moves)
        board.push(random_move)
        if board.is_game_over():
            break
    return board


# Create a dataset using random board positions with given size and analysis depth
# Requires stockfish to work properly
def create_random_dataset(dataset_size: int = 10_000, board_depth: int = 4):
    x_train = []
    y_train = []
    while len(x_train) < dataset_size:
        board = random_board()
        score = stockfish_evaluate(board, board_depth)
        if board is not None and score is not None:  # Stockfish returns 'None' sometimes
            x_train.append(board_to_obs(board))
            y_train.append(score)
            print("\r", end="\r")
            print(f"Dataset Size: {len(x_train)} / {dataset_size}", end="")

    save_dataset(x_train, y_train)
