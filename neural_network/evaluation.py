import math
import os
import random
from datetime import datetime

import chess
import numpy
from keras.models import Sequential, Model
from keras.layers import Dense, Input, Conv2D, Flatten, BatchNormalization, Activation, Add
from keras.optimizers import Adam, RMSprop
from keras.losses import MeanSquaredError
from keras.saving.save import load_model

from database.util import board_to_obs


class BoardEvaluationNetwork:
    model: Sequential

    def __init__(self, model_path: str = None):
        if model_path is not None:
            self.load_model(model_path)

    def create_dense_network(self, size: int, depth: int):
        input_layer = Input(shape=(14, 8, 8))
        x = input_layer
        for _ in range(depth):
            x = Dense(size, activation="relu")(x)
        x = Dense(1, activation="sigmoid")(x)

        self.model = Model(inputs=input_layer, outputs=x)

        self.model.compile(
            optimizer=Adam(
                learning_rate=0.001,
                epsilon=1e-07
            ),
            loss=MeanSquaredError()
        )

    def create_convolutional_network(self, size: int, depth: int):
        input_layer = Input(shape=(14, 8, 8))

        x = input_layer
        for _ in range(depth):
            x = Conv2D(filters=size, kernel_size=3, padding="same", activation="relu", data_format='channels_first')(x)
        x = Flatten()(x)
        x = Dense(64, activation="relu")(x)
        x = Dense(1, activation="sigmoid")(x)

        self.model = Model(inputs=input_layer, outputs=x)

        self.model.compile(
            optimizer=Adam(5e-4),
            loss=MeanSquaredError()
        )

    def create_residual_network(self, size, depth):
        input_layer = Input(shape=(14, 8, 8))

        # adding the convolutional layers
        x = Conv2D(filters=size, kernel_size=3, padding='same', data_format='channels_first')(input_layer)
        for _ in range(depth):
            previous = x
            x = Conv2D(filters=size, kernel_size=3, padding='same', data_format='channels_first')(x)
            x = BatchNormalization()(x)
            x = Activation('relu')(x)
            x = Conv2D(filters=size, kernel_size=3, padding='same', data_format='channels_first')(x)
            x = BatchNormalization()(x)
            x = Add()([x, previous])
            x = Activation('relu')(x)
        x = Flatten()(x)
        x = Dense(1, 'sigmoid')(x)

        self.model = Model(inputs=input_layer, outputs=x)

        self.model.compile(
            optimizer=Adam(5e-4),
            loss=MeanSquaredError()
        )

    def train(self, save_folder: str, x_train, y_train, batch_size=None, epochs=None, steps_per_epoch=None,
              validation_split=0.1,
              callbacks=None):
        print(f"Training model with database of size {len(x_train)}")
        self.model.fit(
            x=x_train,
            y=y_train,
            verbose=1,
            batch_size=batch_size,
            epochs=epochs,
            steps_per_epoch=steps_per_epoch,
            validation_split=validation_split,
            callbacks=callbacks
        )
        self.save_model(save_folder)

    def save_model(self, save_folder: str):
        file_name = "/model_" + datetime.now().strftime("%d_%m_%Y-%H_%M_%S.h5")
        self.model.save(save_folder + file_name)

    def load_model(self, model_path: str):
        if model_path.endswith(".h5"):
            if os.path.exists(model_path):
                try:
                    self.model = load_model(model_path)
                except:
                    raise RuntimeError(f"Unable to load model.")
            else:
                raise FileNotFoundError(f"File {model_path} not found!")
        else:
            raise ValueError(f"Model file is not an '.h5' file.")

    def predict_evaluation(self, board: chess.Board):
        obs = board_to_obs(board)
        obs = numpy.expand_dims(obs, 0)  # Translate shape (None, 8, 8) into shape (14,8,8)
        evaluation = self.model(obs).numpy()[0][0]
        return evaluation

    def get_move(self, board: chess.Board, depth=10):
        evaluations = []
        moves = []
        for move in board.legal_moves:
            board.push(move)
            evaluations.append(self.predict_evaluation(board))
            moves.append(move)
            board.pop()

        max_eval = -math.inf
        index = 0
        for i in range(len(evaluations)):
            if evaluations[i] > max_eval:
                max_eval = evaluations[i]
                index = i

        return moves[index]

    def get_move_minimax(self, board, depth=10):
        moves = []
        best_move = None
        max_evaluation = -numpy.inf

        for move in board.legal_moves:
            board.push(move)
            evaluation = self.minimax(board, depth - 1, -numpy.inf, numpy.inf, False)
            moves.append({
                "move": move,
                "eval": evaluation
            })
            board.pop()
            if evaluation > max_evaluation:
                max_evaluation = evaluation
                best_move = move
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_game_over():
            return self.predict_evaluation(board)

        if maximizing_player:
            max_eval = -numpy.inf
            for move in board.legal_moves:
                board.push(move)
                evaluation = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = numpy.inf
            for move in board.legal_moves:
                board.push(move)
                evaluation = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval
