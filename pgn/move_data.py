import chess
from database.util import pgn_to_games, board_to_obs


# This file is deprecated
# It was used to create and generate training data
# It's contents have been improved and moved to database_pgn.py and database_random.py

def pgn_to_training_data(pgn_file_path: str):
    print("Collecting data...")
    x_train = []
    y_train = []
    games = pgn_to_games(pgn_file_path)
    for game in games:
        x, y = game_to_training_data(game)
        x_train += x
        y_train += y
    return x_train, y_train


FILE_VALUES = {
    "a": 0,
    "b": 1,
    "c": 2,
    "d": 3,
    "e": 4,
    "f": 5,
    "g": 6,
    "h": 7
}


def game_to_training_data(game: chess.pgn.Game):
    x_train = []
    y_train = []

    board = game.board()
    moves = game.mainline_moves()

    for move in moves:
        square_move = board.parse_san(str(move))
        if board.turn == chess.WHITE:
            x = board_to_obs(board)
            y = [square_move.from_square, square_move.to_square]
            x_train.append(x)
            y_train.append(y)
        board.push(square_move)

    return x_train, y_train
