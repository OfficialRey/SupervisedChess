import os.path
import numpy

from chess_api.chess_player import RandomEngine, CustomEngine
from chess_api.default_values import PIECE_IMAGE_PATH, BUTTON_IMAGE_PATH
from database.util import load_datasets, normalize_labels
from gui.interactive_board import InteractiveBoard

from neural_network.evaluation import BoardEvaluationNetwork
from database.database_random import create_random_dataset, random_board, stockfish_evaluate
from database.database_pgn import create_pgn_dataset


def create_dataset(dataset_size=10_000):
    # Create dataset
    create_random_dataset(dataset_size=dataset_size)


def create_convolutional_network(pickle_folder: str, save_folder: str, size: int = 32, depth: int = 4,
                                 epochs: int = 500):
    x_train, y_train = load_datasets(pickle_folder)
    x_train = numpy.array(x_train)
    y_train = normalize_labels(y_train)

    network = BoardEvaluationNetwork()
    network.create_convolutional_network(size, depth)
    network.train(save_folder, x_train, y_train, batch_size=2048, epochs=epochs)
    test_board = random_board()
    network_score = network.predict_evaluation(test_board)
    stockfish_score = stockfish_evaluate(test_board)
    print(f"Predicted Normalized Score: {network_score}")
    print(f"Actual Non-Normalized Score: {stockfish_score}")


def create_residual_network(pickle_folder: str, save_folder: str, size: int = 32, depth: int = 4, epochs: int = 1000):
    x_train, y_train = load_datasets(pickle_folder)
    x_train = numpy.array(x_train)
    y_train = normalize_labels(y_train)

    network = BoardEvaluationNetwork()
    network.create_residual_network(size, depth)
    network.train(save_folder, x_train, y_train, batch_size=2048, epochs=epochs)
    test_board = random_board()
    network_score = network.predict_evaluation(test_board)
    stockfish_score = stockfish_evaluate(test_board)
    print(f"Predicted Normalized Score: {network_score}")
    print(f"Actual Non-Normalized Score: {stockfish_score}")


def play(model_path: str):
    board = InteractiveBoard(button_folder=os.getcwd() + BUTTON_IMAGE_PATH, piece_folder=os.getcwd() + PIECE_IMAGE_PATH,
                             player_1=RandomEngine(), player_2=CustomEngine(
            BoardEvaluationNetwork(model_path)))
    board.run()


def create_pgn_data():
    create_pgn_dataset(pgn_folder=os.getcwd() + "/database/pgn/", save_folder=os.getcwd() + "/datasets/pgn_trained/")


if __name__ == '__main__':
    play("C:/Users/reyof/PycharmProjects/SupervisedChess/models/pgn_trained/normalized_y/convolutional_1000.h5")
    # create_convolutional_network("C:/Users/reyof/PycharmProjects/SupervisedChess/datasets/pgn_data/", "C:/Users/reyof/PycharmProjects/SupervisedChess/models/pgn_trained/", 64, 18, 1000)
