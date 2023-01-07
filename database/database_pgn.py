import os.path

import chess.pgn
from chess import WHITE
from chess.pgn import read_game

from database.util import board_to_obs, stockfish_evaluate, save_dataset


def create_pgn_dataset(pgn_folder: str, save_folder: str):
    x_train = []
    y_train = []
    for files in os.listdir(pgn_folder):
        if files.endswith(".pgn"):
            with open(pgn_folder + files) as pgn:
                while True:
                    print("\r", end="")
                    print(f"Creating dataset: {len(x_train)}", end="")
                    game = read_game(pgn)
                    if game is None:
                        break
                    x, y = game_to_data(game)
                    x_train.extend(x)
                    y_train.extend(y)
    save_dataset(save_folder, x_train, y_train)


def game_to_data(game: chess.pgn.Game):
    x = []
    y = []
    board = chess.Board()
    for move in list(game.mainline_moves()):
        board.push(move)
        if board.turn == WHITE:
            evaluation, success = stockfish_evaluate(board, depth=10)
            if success:
                x.append(board_to_obs(board))
                y.append(evaluation)

    return x, y


if __name__ == '__main__':
    create_pgn_dataset("C:/Users/reyof/PycharmProjects/SupervisedChess/database/pgn/")
