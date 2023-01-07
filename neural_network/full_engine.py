import os

from keras import Model, Input
from keras.losses import MeanSquaredError, MeanSquaredLogarithmicError

from keras.models import Sequential, save_model, load_model
from keras.layers import Dense, ReLU
from keras.optimizers import Adam
from datetime import date


class EngineNetwork:
    model: Model

    def __init__(self):
        pass

    def train(self, x_train, y_train):
        print("Training model.")
        self.model.fit(
            x=x_train,
            y=y_train,
            verbose=2,
            batch_size=64,
            epochs=32
        )
        self.model.save(os.path.curdir + f"/models/model_engine_{date.today()}")

    def predict(self, x):
        pass

    def create_network(self):
        self.model = Sequential([

            # Input layer
            Input((64,)),

            # Hidden Layer
            Dense(256, activation="sigmoid"),
            Dense(256, activation="sigmoid"),
            Dense(128, activation="sigmoid"),
            Dense(128, activation="sigmoid"),

            # Output Layer
            Dense(2, activation="relu")
        ])

        self.model.compile(
            optimizer=Adam(
                learning_rate=0.001,
                epsilon=1e-07,
            ),
            loss=MeanSquaredLogarithmicError(),
            metrics=["accuracy"]
        )
