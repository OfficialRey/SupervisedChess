import dataclasses
import math
import os
import pickle
from datetime import datetime
from typing import List, Any

import chess
import chess.engine
import numpy
from chess.pgn import read_game

# This file is for convenience
# Here one can find values and utility functions about dataset management

DIRECTORY = "datasets"

MAX_GAMES = math.inf

PIECE_VALUES = {
    "P": 1,
    "N": 2,
    "B": 3,
    "R": 4,
    "Q": 5,
    "K": 6
}

squares_index = {
    'a': 0,
    'b': 1,
    'c': 2,
    'd': 3,
    'e': 4,
    'f': 5,
    'g': 6,
    'h': 7
}


# Helper class that will be saved as a pickle file
@dataclasses.dataclass
class DataSet:
    x_train: List[Any]
    y_train: List[Any]


# Retrieves the games from a pgn file with progress output
def pgn_to_games(pgn_file_path: str, max_games=MAX_GAMES):
    if os.path.exists(pgn_file_path):
        if pgn_file_path.endswith(".pgn"):
            games = []
            with open(pgn_file_path, "r") as pgn_file:
                while True and len(games) < max_games:
                    game = read_game(pgn_file)
                    if game is not None:
                        games.append(game)
                        print("\r", end="\r")
                        print(f"Converted Games: {len(games)}", end="")
                    else:
                        break
                pgn_file.close()
            print("\n")
            return games

        else:
            raise RuntimeError(f"The requested file {pgn_file_path} is no pgn file.")
    else:
        raise FileNotFoundError(f"The requested file {pgn_file_path} was not found.")


# This function evaluates a board position using stockfish and returns an int describing how good the position is for white
def stockfish_evaluate(board: chess.Board, depth=10):
    success = True
    with chess.engine.SimpleEngine.popen_uci(os.path.curdir + '/stockfish/stockfish.exe') as sf:
        result = sf.analyse(board, chess.engine.Limit(depth=depth))
        score = result['score'].white().score()
        sf.close()
        if score is None:
            score = 0
            success = False
        return score, success


# Converts a board object to a 14 * 8 * 8 numpy object
# Each 8*8 array describes the appearance of one unique piece type
# Example:
# This would be a pawn starting position described by an 8 * 8 matrix:

# [0,0,0,0,0,0,0,0]
# [0,0,0,0,0,0,0,0]
# [0,0,0,0,0,0,0,0]
# [0,0,0,0,0,0,0,0]
# [0,0,0,0,0,0,0,0]
# [0,0,0,0,0,0,0,0]
# [1,1,1,1,1,1,1,1]
# [0,0,0,0,0,0,0,0]

# This would be a bishop starting position described by an 8 * 8 matrix:
# [0,0,0,0,0,0,0,0]
# [0,0,0,0,0,0,0,0]
# [0,0,0,0,0,0,0,0]
# [0,0,0,0,0,0,0,0]
# [0,0,0,0,0,0,0,0]
# [0,0,0,0,0,0,0,0]
# [0,0,0,0,0,0,0,0]
# [0,0,1,0,0,1,0,0]

# We also include a matrix to describe what pieces are being attacked
# This way the network has to carry less work and might be more accurate

def board_to_obs(board):
    board3d = numpy.zeros((14, 8, 8), dtype=numpy.int8)

    for piece in chess.PIECE_TYPES:
        for square in board.pieces(piece, chess.WHITE):
            idx = numpy.unravel_index(square, (8, 8))
            board3d[piece - 1][7 - idx[0]][idx[1]] = 1
        for square in board.pieces(piece, chess.BLACK):
            idx = numpy.unravel_index(square, (8, 8))
            board3d[piece + 5][7 - idx[0]][idx[1]] = 1
    aux = board.turn
    board.turn = chess.WHITE
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[12][i][j] = 1
    board.turn = chess.BLACK
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[13][i][j] = 1
    board.turn = aux

    return board3d


# Convert a coordinate (a1-h8) to a square int (0-63)
def square_to_index(square):
    letter = chess.square_name(square)
    return 8 - int(letter[1]), squares_index[letter[0]]


# Normalize labels to -1 to 1
# 0 describes an equal position then
# This is done by dividing each value by the highest value of the array
def normalize_labels(y_train: numpy.ndarray):
    return numpy.asarray(y_train / abs(y_train).max() / 2 + 0.5, dtype=numpy.float32)


# Save a dataset to local storage as a pickle file
def save_dataset(pickle_folder: str, x_train, y_train):
    dataset = DataSet(
        x_train=x_train,
        y_train=y_train
    )
    file_name = datetime.now().strftime("%d_%m_%Y-%H_%M_%S.pickle")
    with open(f"{pickle_folder}/{file_name}", "wb") as file:
        pickle.dump(dataset, file)
        file.close()


# Load a dataset from local storage as a pickle file
def load_datasets(pickle_folder: str):
    x_train = []
    y_train = []
    path = pickle_folder
    for file in os.listdir(path):
        if file.endswith(".pickle"):
            with open(path + file, "rb") as pickle_file:
                data = pickle.load(pickle_file)
                x_train += data.x_train
                y_train += data.y_train
    x_train = numpy.asarray(x_train)
    y_train = numpy.array(y_train)
    return x_train, y_train
