import chess
from stockfish import Stockfish


class ChessAPI:
    def __init__(self, engine_depth=24, engine_threads=2, engine_hash=2048):
        self.stockfish = Stockfish(
            path="/stockfish/stockfish.exe",
            depth=engine_depth,
            parameters={
                "Threads": engine_threads,
                "Hash": engine_hash
            })
        self.board = chess.Board()

    def reset_board(self):
        self.board.reset_board()
        self.stockfish.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")

    def make_move(self, move:  str):
        if self.is_move_legal(move):
            print("Legal move")
            self.board.push(get_move_from_algebraic(move))
            self.stockfish.make_moves_from_current_position([move])

    def is_move_legal(self, move: str) -> bool:
        return self.board.is_legal(get_move_from_algebraic(move))

    def is_game_end(self) -> bool:
        return self.board.is_checkmate() or self.board.is_stalemate() or self.board.is_variant_draw()

    def get_obs(self):
        return 0

    def get_best_engine_move(self) -> str:
        return self.stockfish.get_best_move()


def get_move_from_algebraic(move: str) -> chess.Move:
    from_square = get_square_from_algebraic(move[:2])
    to_square = get_square_from_algebraic(move[2:])
    return chess.Move(from_square, to_square)


files = ["a", "b", "c", "d", "e", "f", "g", "h"]


def get_square_from_algebraic(square: str) -> int:
    file = files.index(square[0])
    rank = int(square[1]) - 1
    return rank * 8 + file


if __name__ == '__main__':
    chess_api = ChessAPI()
    for i in range(4):
        move = chess_api.get_best_engine_move()
        chess_api.make_move(move)
