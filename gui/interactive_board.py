import random
import sys
import time
import traceback

import chess
import pygame

from chess_api.chess_player import ChessPlayer, CustomEngine
from chess_api.default_values import RANKS, FILES, BOARD_GREEN, BOARD_WHITE, SQUARE_SIZE, SCREEN_SIZE, BLACK, \
    PIECE_SIZE, GRAY, INFO_SPACE, LINE_THICKNESS, AUTO_MOVE_TIME, WHITE, BRIGHTEN_EFFECT, DARKEN_EFFECT, LIGHT_GRAY, \
    MOVES_PER_ROW, MOVE_DISTANCE, BOARD_WIDTH, BOARD_HEIGHT
from database.database_random import stockfish_evaluate


class InteractiveBoard:

    def __init__(self, piece_folder: str, button_folder: str, player_1: ChessPlayer, player_2: ChessPlayer, gfx=False):
        self.gfx = gfx
        self.piece_folder = piece_folder
        self.button_folder = button_folder
        self.board = chess.Board()
        self.moves = []
        self.last_move_time = time.time()
        self.players = [player_1, player_2]
        self.san_moves = ""
        self.index = 0  # Index for current board
        self.stockfish_evaluation = 0
        self.paused = True
        self.buttons = [
            RestartButton(int(SCREEN_SIZE[0] - INFO_SPACE + 20), int(SCREEN_SIZE[1] - 80),
                          button_folder + "restart.png", 3),
            PlayPauseButton(int(SCREEN_SIZE[0] - INFO_SPACE + 80), int(SCREEN_SIZE[1] - 80), button_folder + "play.png",
                            button_folder + "pause.png", 3),
            PreviousButton(int(SCREEN_SIZE[0] - INFO_SPACE + 140), int(SCREEN_SIZE[1] - 80),
                           button_folder + "previous.png", 3),
            NextButton(int(SCREEN_SIZE[0] - INFO_SPACE + 200), int(SCREEN_SIZE[1] - 80), button_folder + "next.png", 3)
        ]
        pygame.init()
        self.window = pygame.display.set_mode(SCREEN_SIZE)
        self.big_font = pygame.font.SysFont("arial.ttf", 48)
        self.san_font = pygame.font.SysFont("arial.ttf", 30)
        pygame.display.set_caption("Chess AI")
        pygame.mixer.init()

    def reset(self):
        self.last_move_time = time.time()
        random.shuffle(self.players)
        self.moves = []
        self.san_moves = ""
        self.board = chess.Board()
        self.index = 0  # Index for current board
        self._update()

    def run(self):
        self.reset()
        while True:
            time.sleep(0.01)  # Save CPU lifetime
            self._calculate_events()
            self._update_frame()

    def _update_frame(self):
        self._auto_move()
        self._render_buttons()
        pygame.display.update()

    def _auto_move(self):
        if not self.paused:
            if self.seconds_since_last_move() >= AUTO_MOVE_TIME:
                self._play_next_move()

    def _play_next_move(self):
        player: ChessPlayer
        if len(self.moves) % 2 == 0:
            player = self.players[0]
        else:
            player = self.players[1]
        self.play_move(player.get_move(self.board))

    def seconds_since_last_move(self):
        return time.time() - self.last_move_time

    def _calculate_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

    def play_move(self, move: chess.Move):
        if self.board.is_legal(move):
            self.last_move_time = time.time()
            if self.board.turn == chess.WHITE:
                self.san_moves += f" {(len(self.moves) // 2 + 1)}."
            self.san_moves += " " + self.board.san(move)
            self.board.push(move)
            self.moves.append(move)
            self.index += 1
            self._update()

    def update_evaluation(self):
        self.stockfish_evaluation, success = stockfish_evaluate(board=self.board, depth=10)

    def _update(self):
        self._render_board()
        self._render_board_lines()
        self._render_pieces()
        self._render_info()

        pygame.display.update()

    def _test_render_speed(self):
        start = time.time()
        self._render_board()
        render_board = time.time() - start
        render_sum = render_board
        print(f"Render Board: {render_board}")

        start = time.time()
        self._render_board_lines()
        render_lines = time.time() - start
        render_sum += render_lines
        print(f"Render Board Lines: {render_lines}")

        start = time.time()
        self._render_pieces()
        render_pieces = time.time() - start
        render_sum += render_pieces
        print(f"Render Pieces: {render_pieces}")

        start = time.time()
        self._render_player_info()
        render_info = time.time() - start
        render_sum += render_info
        print(f"Render Info: {render_info}")
        print(f"Sum: {render_sum}")
        print()

    def play(self):
        if len(self.moves) > self.index + 1:
            for i in range(self.index, len(self.moves)):
                self.board.push(self.moves[i])
                self.index = i
        self._update()
        self.paused = False

    def pause(self):
        self.paused = True

    def previous_position(self):
        self.paused = True
        if self.index > 0:
            self.index -= 1
            self.board.pop()
            self._update()

    def next_position(self):
        self.paused = True
        if self.index < len(self.moves):
            self.board.push(self.moves[self.index])
            self.index += 1
        else:
            self._play_next_move()
        self._update()

    def _render_board(self):
        for ranks in range(RANKS):
            for files in range(FILES):
                color = BOARD_WHITE if ranks % 2 == files % 2 else BOARD_GREEN
                self._render_square(files, ranks, color)
        pygame.draw.rect(self.window, GRAY, pygame.Rect(SCREEN_SIZE[0] - INFO_SPACE, 0, INFO_SPACE, SCREEN_SIZE[1]))
        pygame.draw.line(self.window, BLACK, (SCREEN_SIZE[0] - INFO_SPACE + (LINE_THICKNESS // 2) - 1, 0),
                         (SCREEN_SIZE[0] - INFO_SPACE + (LINE_THICKNESS // 2) - 1, SCREEN_SIZE[1]), LINE_THICKNESS)

    def _render_square(self, file, rank, color):
        pygame.draw.rect(self.window, color,
                         pygame.Rect(file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def _render_board_lines(self):
        if self.gfx:
            for ranks in range(RANKS):
                for files in range(FILES):
                    pygame.draw.line(self.window, BLACK,
                                     (files * SQUARE_SIZE + (LINE_THICKNESS // 2), ranks * SQUARE_SIZE),
                                     (files * SQUARE_SIZE + (LINE_THICKNESS // 2), ranks * SQUARE_SIZE + SQUARE_SIZE),
                                     LINE_THICKNESS)
                    pygame.draw.line(self.window, BLACK,
                                     (files * SQUARE_SIZE + (LINE_THICKNESS // 2), ranks * SQUARE_SIZE),
                                     (files * SQUARE_SIZE + SQUARE_SIZE + (LINE_THICKNESS // 2), ranks * SQUARE_SIZE),
                                     LINE_THICKNESS)

    def _render_pieces(self):
        for rank in range(RANKS):
            for file in range(FILES):
                square = rank * 8 + file
                piece = self.board.piece_at(square)
                if piece is not None:
                    piece_name = f"{piece}{'w' if piece.color else 'b'}"
                    self._render_piece(piece_name, file, rank)

    def _render_piece(self, piece_name, file, rank):
        image = pygame.image.load(self.piece_folder + piece_name.lower() + ".png").convert_alpha()
        width = image.get_width() * PIECE_SIZE
        height = image.get_height() * PIECE_SIZE
        image = pygame.transform.scale(image, (width, height))
        self.window.blit(image, (
            file * SQUARE_SIZE, BOARD_HEIGHT - rank * SQUARE_SIZE - SQUARE_SIZE))

    def _render_info(self):
        self._render_player_info()
        self._render_evaluation_info()
        self.render_move_info()

    def _render_player_info(self):
        # Engine Info
        white = self.big_font.render(f"White: {self.players[0].__name__}", True, WHITE)
        black = self.big_font.render(f"Black: {self.players[1].__name__}", True, BLACK)
        self.window.blit(white, (SCREEN_SIZE[0] - INFO_SPACE + 20, 20))
        self.window.blit(black, (SCREEN_SIZE[0] - INFO_SPACE + 20, 60))

    def _render_evaluation_info(self):
        # Evaluation Info
        self.update_evaluation()
        graph_length = (SCREEN_SIZE[0] - 20) - (SCREEN_SIZE[0] - INFO_SPACE + 20)
        evaluation = self.stockfish_evaluation / 100

        white_length = graph_length / 2 + (evaluation * 10)
        if white_length > graph_length:
            white_length = graph_length
        black_length = graph_length - white_length

        pygame.draw.rect(self.window, LIGHT_GRAY,
                         pygame.Rect(SCREEN_SIZE[0] - INFO_SPACE + 15, 115, graph_length + 10, 50))
        pygame.draw.rect(self.window, WHITE, pygame.Rect(SCREEN_SIZE[0] - INFO_SPACE + 20, 120, white_length, 40))
        pygame.draw.rect(self.window, BLACK,
                         pygame.Rect(SCREEN_SIZE[0] - INFO_SPACE + 20 + white_length, 120, black_length, 40))
        pygame.draw.line(self.window, LIGHT_GRAY,
                         (SCREEN_SIZE[0] - INFO_SPACE + 20 + graph_length / 2 - LINE_THICKNESS / 2, 120),
                         (SCREEN_SIZE[0] - INFO_SPACE + 20 + graph_length / 2 - LINE_THICKNESS / 2, 160),
                         LINE_THICKNESS)
        if evaluation != 0:
            color = BLACK if evaluation > 0 else WHITE
            evaluation_font = self.big_font.render(str(evaluation), True, color)
            x_pos = SCREEN_SIZE[0] - INFO_SPACE + 30 if evaluation > 0 else SCREEN_SIZE[
                                                                                0] - 30 - evaluation_font.get_width()
            height = evaluation_font.get_height()
            self.window.blit(evaluation_font, (x_pos, 110 + height / 2))

    def render_move_info(self):
        # Convert san-moves to list of lists of moves of size 8
        move_data = self.san_moves.split(" ")[1::]
        moves = []
        for i in range(0, len(move_data), 3):
            moves.append(f"{move_data[i]} {move_data[i + 1]}")
            if not i + 3 > len(move_data):
                moves.append(move_data[i + 2])
        rows = list(self._split_moves(moves, 8))

        # Convert san to images
        images = []
        for move in rows:
            for san in move:
                images.append(self.san_font.render(san, True, BLACK))

        # Display images & highlight current shown position
        distance = 0
        for i in range(len(images)):
            if i % 8 == 0:
                distance = 0
            x = SCREEN_SIZE[0] - INFO_SPACE + 20 + distance
            y = 220 + (40 * int(i / MOVES_PER_ROW))

            if i == self.index - 1:
                pygame.draw.rect(self.window, LIGHT_GRAY,
                                 pygame.Rect(x, y, images[i].get_width(),
                                             images[i].get_height()))
            self.window.blit(images[i], (x, y))

            distance += images[i].get_width() + MOVE_DISTANCE

    def _split_moves(self, move_list, moves_per_row):
        for i in range(0, len(move_list), moves_per_row):
            yield move_list[i:i + moves_per_row]

    def _render_buttons(self):
        for button in self.buttons:
            button.render(self.window, self)


class ChessButton:

    def __init__(self, x, y, image_path, scale):
        self.x = x
        self.y = y
        self.rect = None
        self.image = None
        self.scale = scale
        self.clicked = False
        self.load_image(image_path)

    def load_image(self, image_path):
        image = pygame.image.load(image_path)
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * self.scale), int(height * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def render(self, surface, board: InteractiveBoard):
        image = self.image.copy()
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            # Animate
            if self.clicked is False:
                image = self.highlight_image(image, BRIGHTEN_EFFECT)
                if pygame.mouse.get_pressed()[0] == 1:
                    self.clicked = True
                    self.click(board)
            else:
                image = self.highlight_image(image, DARKEN_EFFECT)

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

        surface.blit(image, (self.rect.x, self.rect.y))

    def highlight_image(self, image, factor):
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                pos = (x, y)
                r, g, b, alpha = image.get_at(pos)
                r = 255 if r * factor > 255 else r * factor
                g = 255 if g * factor > 255 else g * factor
                b = 255 if g * factor > 255 else b * factor
                color = (r, g, b, alpha)
                image.set_at(pos, color)
        return image

    def click(self, board: InteractiveBoard):
        raise NotImplementedError


class PlayPauseButton(ChessButton):

    def __init__(self, x, y, play_image_path, pause_image_path, scale):
        super().__init__(x, y, play_image_path, scale)
        self.play_image = play_image_path
        self.pause_image = pause_image_path

    def click(self, board):
        if board.paused:
            board.play()
            self.load_image(self.pause_image)
        else:
            board.pause()
            self.load_image(self.play_image)


class PreviousButton(ChessButton):
    def click(self, board):
        board.previous_position()


class NextButton(ChessButton):
    def click(self, board):
        board.next_position()


class RestartButton(ChessButton):
    def click(self, board):
        board.reset()
