from typing import List

import chess
import chess.pgn

from stockfish import Stockfish


class StockFishEngine:
    files = ["a", "b", "c", "d", "e", "f", "g", "h"]

    def __init__(self, engine_depth=24, engine_threads=2, engine_hash=2048, uci_elo=4200):
        self.engine = Stockfish(
            path="/stockfish/stockfish.exe",
            depth=engine_depth,
            parameters={
                "Threads": engine_threads,
                "Hash": engine_hash,
                "UCI_Elo": uci_elo
            })
        self.engine.set_elo_rating(4200)
        self.board = chess.Board()
        self.moves = []

    def reset_board(self):
        self.board.reset_board()
        self.engine.set_position(None)
        self.moves = []

    def set_fen(self, fen):
        self.engine.set_fen_position(fen)
        self.board.set_fen(fen)

    def make_moves(self, moves: List[chess.Move]) -> bool:
        for move in moves:
            if not self.make_move(move):
                return False
        return True

    def make_move(self, move: chess.Move) -> bool:
        if self.is_move_legal(move):
            self.engine.make_moves_from_current_position([move.uci()])
            self.board.push(move)
            self.moves.append(move.uci())
            return True
        else:
            return False

    def is_move_legal(self, move: chess.Move):
        return self.board.is_legal(move)

    def get_legal_moves(self):
        return self.board.legal_moves

    def get_moves_played(self):
        return self.moves

    def evaluate_current_position(self):
        return self.engine.get_evaluation()

    def evaluate_position(self, board: chess.Board):
        current_fen = self.board.fen()
        self.engine.set_fen_position(board.fen())
        evaluation = self.engine.get_evaluation()
        self.engine.set_fen_position(current_fen)
        return evaluation
