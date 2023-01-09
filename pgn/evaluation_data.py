import dataclasses
import math
import pickle
from typing import List
import datetime

import chess
import numpy

from database.util import pgn_to_games, board_to_obs
from .fen_generator import get_random_fen_from_games, get_random_fen
from stockfish_api import StockFishEngine


# This file is deprecated
# It was used to create and generate training data


# It is very similar to database_pgn.py and database_random.py and therefore not documented
@dataclasses.dataclass
class EvaluationDenseTrainingData:
    x_train: List[List[int]]
    y_train: List[int]


@dataclasses.dataclass
class EvaluationConvolutionalTrainingData:
    x_train: numpy.ndarray
    y_train: numpy.ndarray


def pgn_to_convolutional_training_data(pgn_file_path, dataset_size: int = math.inf):
    print("Collecting data...")
    x_train, y_train = load_training_data(f"evaluation_convolutional_{datetime.date.today()}.pickle")
    x_train = list(x_train)
    y_train = list(y_train)
    games = pgn_to_games(pgn_file_path)
    stockfish_engine = StockFishEngine(
        engine_depth=4,
        engine_threads=2,
        engine_hash=1024
    )
    try:
        while True:
            fen = get_random_fen_from_games(games)
            print("\r", end="\r")
            print(f"Dataset: {len(x_train)} | Fen: {fen}", end="")
            if fen is not None:
                x, y = fen_to_convolutional_training_data(fen, stockfish_engine)
                x_train.append(x)
                y_train.append(y)
    except KeyboardInterrupt:
        # Save Data
        x_train = numpy.array(x_train)
        y_train = numpy.array(y_train)
        data = EvaluationConvolutionalTrainingData(x_train=x_train, y_train=y_train)
        with open(f"evaluation_convolutional_{datetime.date.today()}.pickle", "wb") as file:
            pickle.dump(data, file)
            file.close()

        return x_train, y_train


def random_training_data(dataset_size: int = math.inf):
    x_train = []
    y_train = []
    stockfish_engine = StockFishEngine(
        engine_depth=4,
        engine_threads=2,
        engine_hash=1024
    )
    for i in range(dataset_size):
        print("\r", end="\r")
        print(f"Dataset: {len(x_train)}", end="")
        fen = get_random_fen()
        x, y = fen_to_training_data(fen, stockfish_engine)
        x_train.append(x)
        y_train.append(y)

    # Save data
    data = EvaluationDenseTrainingData(x_train=x_train, y_train=y_train)
    with open(f"{datetime.date.today()}", "w") as file:
        pickle.dump(data, file)
        file.close()


def load_training_data(pickle_path):
    with open(pickle_path, "rb") as file:
        evaluation = pickle.load(file)
        x_train = evaluation.x_train
        y_train = evaluation.y_train
        return x_train, y_train


def pgn_to_training_data(pgn_file_path: str, dataset_size: int = math.inf):
    print("Collecting data...")
    x_train = []
    y_train = []
    games = pgn_to_games(pgn_file_path)
    stockfish_engine = StockFishEngine(
        engine_depth=4,
        engine_threads=2,
        engine_hash=1024
    )
    for i in range(dataset_size):
        fen = get_random_fen_from_games(games)
        print("\r", end="\r")
        print(f"Dataset: {len(x_train)} | Fen: {fen}", end="")
        if fen is not None:
            x, y = fen_to_training_data(fen, stockfish_engine)
            x_train.append(x)
            y_train.append(y)

    # Save Data
    data = EvaluationDenseTrainingData(x_train=x_train, y_train=y_train)
    with open(f"evaluation_{datetime.date.today()}.pickle", "wb") as file:
        pickle.dump(data, file)
        file.close()

    return x_train, y_train


def fen_to_training_data(fen: str, stockfish_engine: StockFishEngine):
    board = chess.Board()
    board.set_fen(fen)
    return board_to_obs(board), stockfish_engine.evaluate_position(board)["value"]


def fen_to_convolutional_training_data(fen: str, stockfish_engine: StockFishEngine):
    board = chess.Board()
    board.set_fen(fen)
    return board_to_obs(board), stockfish_engine.evaluate_position(board)["value"]
