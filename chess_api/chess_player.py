import random

import chess
from keras.models import Model

from neural_network.evaluation import BoardEvaluationNetwork


# An interface for the Interactive Board
# Used to transform bots, humans and engines into a usable player easily
class ChessPlayer:
    def __init__(self, is_human=False):
        self.is_human = is_human

    def get_move(self, board: chess.Board):
        raise NotImplementedError


# An engine that just does anything
class RandomEngine(ChessPlayer):

    def __init__(self):
        super().__init__()
        self.__name__ = "Random Move Engine"

    def get_move(self, board: chess.Board):
        return random.choice(list(board.legal_moves))


# A custom engine using the board evaluation network
class CustomEngine(ChessPlayer):
    def __init__(self, model: BoardEvaluationNetwork):
        super().__init__()
        self.model = model
        self.__name__ = "Custom Engine"

    def get_move(self, board: chess.Board):
        return self.model.get_move(board)
        # return self.model.get_move_minimax(board, depth=1)
