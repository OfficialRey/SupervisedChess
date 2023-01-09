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


# This file is used to communicate between the user and the engines.
# Its features are a handy gui, sprites, move selection, an autoplay function, board evaluation,
# move history with algebraic notation, a pause and a reset function.
# It also features an interface to communicate with a board and custom-made chess engines.
class InteractiveBoard:

    # When initializing a board certain locations have to be set for the computer to find the images.
    # The custom engines also have to be set
    # gfx is a deprecated option to enable line drawing in between squares
    def __init__(self, piece_folder: str, button_folder: str, player_1: ChessPlayer, player_2: ChessPlayer, gfx=False):
        # Used for the deprecated rendering feature
        self.gfx = gfx

        # Folders used for images
        self.piece_folder = piece_folder
        self.button_folder = button_folder

        # The chess board
        self.board = chess.Board()

        # We store all the moves and the current move index to keep track of previous board states
        self.moves = []
        self.san_moves = ""
        self.index = 0  # Index for current board

        # The move time is used for autoplay
        self.last_move_time = time.time()

        # We store the players in an array, so we can shuffle the positions easily anytime
        self.players = [player_1, player_2]

        # We store the stockfish evaluation so that we don't have to ask stockfish for its evaluation every frame
        self.stockfish_evaluation = 0

        # Whether the game is paused or not - pretty self explanatory
        self.paused = True

        # Here we initialise the buttons to be used in the gui
        # I drew the buttons myself so there are no copyright restrictions
        self.buttons = [
            RestartButton(int(SCREEN_SIZE[0] - INFO_SPACE + 20), int(SCREEN_SIZE[1] - 80),
                          button_folder + "restart.png", 3),
            PlayPauseButton(int(SCREEN_SIZE[0] - INFO_SPACE + 80), int(SCREEN_SIZE[1] - 80), button_folder + "play.png",
                            button_folder + "pause.png", 3),
            PreviousButton(int(SCREEN_SIZE[0] - INFO_SPACE + 140), int(SCREEN_SIZE[1] - 80),
                           button_folder + "previous.png", 3),
            NextButton(int(SCREEN_SIZE[0] - INFO_SPACE + 200), int(SCREEN_SIZE[1] - 80), button_folder + "next.png", 3)
        ]

        # Pygame initialisation
        # We use pygame for convenience
        pygame.init()
        self.window = pygame.display.set_mode(SCREEN_SIZE)
        self.big_font = pygame.font.SysFont("arial.ttf", 48)
        self.san_font = pygame.font.SysFont("arial.ttf", 30)
        pygame.display.set_caption("Chess AI")
        pygame.mixer.init()

    # Resets the board and stored information to start a fresh game
    def reset(self):
        self.last_move_time = time.time()
        random.shuffle(self.players)
        self.moves = []
        self.san_moves = ""
        self.board = chess.Board()
        self.index = 0
        self._update()

    # Driver method to keep the game going
    def run(self):
        self.reset()
        while True:
            time.sleep(0.01)  # Save CPU lifetime
            self._calculate_events()
            self._update_frame()

    # Renders the next frame onto the screen and forces a pygame update
    def _update_frame(self):
        self._auto_move()
        self._render_buttons()
        pygame.display.update()

    # Autoplay function. Pushes a piece every second
    def _auto_move(self):
        if not self.paused:
            if self.seconds_since_last_move() >= AUTO_MOVE_TIME:
                self._play_next_move()

    # Plays the next move according to whose turn it is
    def _play_next_move(self):
        player: ChessPlayer
        if len(self.moves) % 2 == 0:
            player = self.players[0]
        else:
            player = self.players[1]
        self.play_move(player.get_move(self.board))

    # We have to know when autoplay has to make the next move
    def seconds_since_last_move(self):
        return time.time() - self.last_move_time

    # Pygame comes with an event system out of the box
    # We use it here for convenience and keep track of the window state
    def _calculate_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

    # Makes a move, but validates it first
    # We also save the moves we make to a list
    # This way we can keep track of previous board positions and can show the algebraic notations of moves
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

    # We ask stockfish about its evaluation for the current board position
    def update_evaluation(self):
        self.stockfish_evaluation, success = stockfish_evaluate(board=self.board, depth=10)

    # Renders the content on the pygame surface and forces it to update
    def _update(self):
        self._render_board()
        self._render_board_lines()
        self._render_pieces()
        self._render_info()

        pygame.display.update()

    # Debug method
    # Before setting a fixed stockfish evaluation as a class attribute the program was very slow
    # This was used to find the solution
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

    # Enables autoplay
    # Since the user could be in one of the many previous positions we have to ensure that our board index is right
    # Therefore we have to get in the correct position first by iterating over all the upcoming moves and playing them
    def play(self):
        if len(self.moves) > self.index + 1:
            for i in range(self.index, len(self.moves)):
                self.board.push(self.moves[i])
                self.index = i
        self._update()
        self.paused = False

    # Disables autoplay
    def pause(self):
        self.paused = True

    # Steps to the previous board position
    def previous_position(self):
        self.paused = True
        if self.index > 0:
            self.index -= 1
            self.board.pop()
            self._update()

    # Steps to the next board position
    # Plays the next move if already on the last played move
    def next_position(self):
        self.paused = True
        if self.index < len(self.moves):
            self.board.push(self.moves[self.index])
            self.index += 1
        else:
            self._play_next_move()
        self._update()

    # The following code is gui.py implemented in this class with slight changes
    # There is additional functionality below though

    # Renders the board
    def _render_board(self):
        for ranks in range(RANKS):
            for files in range(FILES):
                color = BOARD_WHITE if ranks % 2 == files % 2 else BOARD_GREEN
                self._render_square(files, ranks, color)
        pygame.draw.rect(self.window, GRAY, pygame.Rect(SCREEN_SIZE[0] - INFO_SPACE, 0, INFO_SPACE, SCREEN_SIZE[1]))
        pygame.draw.line(self.window, BLACK, (SCREEN_SIZE[0] - INFO_SPACE + (LINE_THICKNESS // 2) - 1, 0),
                         (SCREEN_SIZE[0] - INFO_SPACE + (LINE_THICKNESS // 2) - 1, SCREEN_SIZE[1]), LINE_THICKNESS)

    # Renders squares
    def _render_square(self, file, rank, color):
        pygame.draw.rect(self.window, color,
                         pygame.Rect(file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Renders board lines in between squares
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

    # Renders the pieces to the pygame surface
    def _render_pieces(self):
        for rank in range(RANKS):
            for file in range(FILES):
                square = rank * 8 + file
                piece = self.board.piece_at(square)
                if piece is not None:
                    piece_name = f"{piece}{'w' if piece.color else 'b'}"
                    self._render_piece(piece_name, file, rank)

    # Renders one piece to the pygame surface
    def _render_piece(self, piece_name, file, rank):
        image = pygame.image.load(self.piece_folder + piece_name.lower() + ".png").convert_alpha()
        width = image.get_width() * PIECE_SIZE
        height = image.get_height() * PIECE_SIZE
        image = pygame.transform.scale(image, (width, height))
        self.window.blit(image, (
            file * SQUARE_SIZE, BOARD_HEIGHT - rank * SQUARE_SIZE - SQUARE_SIZE))

    # The following code snippets are entirely new regarding gui.py

    # Render additional info about the current game
    def _render_info(self):
        self._render_player_info()
        self._render_evaluation_info()
        self.render_move_info()

    # Here we use pygame's font object to create images for our player names and render them to the surface
    def _render_player_info(self):
        # Engine Info
        white = self.big_font.render(f"White: {self.players[0].__name__}", True, WHITE)
        black = self.big_font.render(f"Black: {self.players[1].__name__}", True, BLACK)
        self.window.blit(white, (SCREEN_SIZE[0] - INFO_SPACE + 20, 20))
        self.window.blit(black, (SCREEN_SIZE[0] - INFO_SPACE + 20, 60))

    # Here we ask stockfish about the current evaluation and draw a bar that represents that value
    def _render_evaluation_info(self):
        # Evaluation Info
        self.update_evaluation()
        # Set graph data
        graph_length = (SCREEN_SIZE[0] - 20) - (SCREEN_SIZE[0] - INFO_SPACE + 20)
        evaluation = self.stockfish_evaluation / 100

        white_length = graph_length / 2 + (evaluation * 10)
        if white_length > graph_length:
            white_length = graph_length
        black_length = graph_length - white_length

        # Draw bar and border around
        pygame.draw.rect(self.window, LIGHT_GRAY,
                         pygame.Rect(SCREEN_SIZE[0] - INFO_SPACE + 15, 115, graph_length + 10, 50))
        pygame.draw.rect(self.window, WHITE, pygame.Rect(SCREEN_SIZE[0] - INFO_SPACE + 20, 120, white_length, 40))
        pygame.draw.rect(self.window, BLACK,
                         pygame.Rect(SCREEN_SIZE[0] - INFO_SPACE + 20 + white_length, 120, black_length, 40))
        pygame.draw.line(self.window, LIGHT_GRAY,
                         (SCREEN_SIZE[0] - INFO_SPACE + 20 + graph_length / 2 - LINE_THICKNESS / 2, 120),
                         (SCREEN_SIZE[0] - INFO_SPACE + 20 + graph_length / 2 - LINE_THICKNESS / 2, 160),
                         LINE_THICKNESS)
        # If stockfish doesn't like the current position it will return 0
        # (it actually will not - I just mapped a None output to 0 so that I don't get wrong datasets / errors)

        # If the evaluation is not "None" / 0 it will use pygame's font system to draw
        # the text representing the evaluation on top of the bar
        if evaluation != 0:
            color = BLACK if evaluation > 0 else WHITE
            evaluation_font = self.big_font.render(str(evaluation), True, color)
            x_pos = SCREEN_SIZE[0] - INFO_SPACE + 30 if evaluation > 0 else SCREEN_SIZE[
                                                                                0] - 30 - evaluation_font.get_width()
            height = evaluation_font.get_height()
            self.window.blit(evaluation_font, (x_pos, 110 + height / 2))

    # Renders moves in algebraic notation below the evaluation bar
    def render_move_info(self):
        # Convert san-moves to list of lists of moves of size 8
        # 8 moves per row

        # We also manipulate the junk of strings to separate moves from numbers and whitespaces
        move_data = self.san_moves.split(" ")[1::]
        moves = []
        for i in range(0, len(move_data), 3):
            moves.append(f"{move_data[i]} {move_data[i + 1]}")
            if not i + 3 > len(move_data):
                moves.append(move_data[i + 2])
        rows = list(self._split_moves(moves, 8))

        # Convert san strings to images using pygame's font object
        images = []
        for move in rows:
            for san in move:
                images.append(self.san_font.render(san, True, BLACK))

        # Display images & highlight current shown position
        distance = 0
        for i in range(len(images)):
            if i % 8 == 0:
                distance = 0
            # We align the moves on a grid to ensure they won't clip out of the surface
            x = SCREEN_SIZE[0] - INFO_SPACE + 20 + distance
            y = 220 + (40 * int(i / MOVES_PER_ROW))

            # Draw a rectangle to highlight what move was played.
            # This is for user convenience since it allows to see the current board position and move index
            if i == self.index - 1:
                pygame.draw.rect(self.window, LIGHT_GRAY,
                                 pygame.Rect(x, y, images[i].get_width(),
                                             images[i].get_height()))
            self.window.blit(images[i], (x, y))

            distance += images[i].get_width() + MOVE_DISTANCE

    # Helper function to split moves
    def _split_moves(self, move_list, moves_per_row):
        for i in range(0, len(move_list), moves_per_row):
            yield move_list[i:i + moves_per_row]

    # Renders the buttons and thereby enables their functionality
    def _render_buttons(self):
        for button in self.buttons:
            button.render(self.window, self)


# A basic class that represents a button
# Uses sprites
class ChessButton:

    def __init__(self, x, y, image_path, scale):
        self.x = x
        self.y = y
        self.rect = None
        self.image = None
        self.scale = scale
        self.clicked = False
        self.load_image(image_path)

    # Load an image and crop it using a scale
    def load_image(self, image_path):
        image = pygame.image.load(image_path)
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * self.scale), int(height * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    # Render the button on a surface and interact with a board
    def render(self, surface, board: InteractiveBoard):
        # We copy the image and work with the copy to not lose its original state
        image = self.image.copy()
        pos = pygame.mouse.get_pos()

        # Check mouse collision
        if self.rect.collidepoint(pos):
            # Add some fancy animations to increase user responsiveness
            # (we actually just change the brightness - but it works)
            if self.clicked is False:
                image = self.highlight_image(image, BRIGHTEN_EFFECT)
                if pygame.mouse.get_pressed()[0] == 1:
                    # Clicked bool system so the button does not get spammed when holding mouse click over it
                    self.clicked = True
                    self.click(board)
            else:
                image = self.highlight_image(image, DARKEN_EFFECT)

            if pygame.mouse.get_pressed()[0] == 0:
                # Let go if it is not pressed
                self.clicked = False

        # Render the button
        surface.blit(image, (self.rect.x, self.rect.y))

    # We highlight the image using a brightness method
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

    # Since we want other classes to extend this one we want to deny raw usage of it
    def click(self, board: InteractiveBoard):
        raise NotImplementedError


# Play and pause functionality using the ChessButton class
class PlayPauseButton(ChessButton):

    def __init__(self, x, y, play_image_path, pause_image_path, scale):
        super().__init__(x, y, play_image_path, scale)
        self.play_image = play_image_path
        self.pause_image = pause_image_path

    # Extend click method of ChessButton
    # We also change images to increase responsiveness and feedback
    def click(self, board):
        if board.paused:
            board.play()
            self.load_image(self.pause_image)
        else:
            board.pause()
            self.load_image(self.play_image)


# Steps back one board position
class PreviousButton(ChessButton):
    def click(self, board):
        board.previous_position()


# Steps ahead one position / plays the next move
class NextButton(ChessButton):
    def click(self, board):
        board.next_position()


# Resets the board entirely
class RestartButton(ChessButton):
    def click(self, board):
        board.reset()
