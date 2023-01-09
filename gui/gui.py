import chess
import pygame

from chess_api.default_values import SQUARE_SIZE, BLACK, RANKS, FILES, BOARD_GREEN, BOARD_WHITE, SCREEN_SIZE, \
    PIECE_SIZE

# WARNING: This file is deprecated
# Contents have moved to interactive_board.py

# This file is used to render and draw the gui of the chess board
# Additional information will also be rendered
# This is very helpful to monitor the engine's performance and get a better understanding of its actions

# We use pygame for convenience
window = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Chess AI")
pygame.mixer.init()


# Driver method to render a board
def render_board(board: chess.Board) -> None:
    draw_board()
    draw_board_lines()
    draw_pieces(board)
    update_screen()


# draw the squares of a board using white and green colors
# This is a subjective topic, but I think it is easier to understand the board using green instead of black
def draw_board():
    for ranks in range(RANKS):
        for files in range(FILES):
            color = BOARD_GREEN if ranks % 2 == files % 2 else BOARD_WHITE
            draw_square(files, ranks, color)


# Helper method to draw a square onto the surface used by pygame
def draw_square(file, rank, color):
    pygame.draw.rect(window, color,
                     pygame.Rect(file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


# Draw lines to better distinguish the squares
# This function was used but then became deprecated since it looked bad
def draw_board_lines():
    for ranks in range(RANKS):
        for files in range(FILES):
            pygame.draw.line(window, BLACK, (files * SQUARE_SIZE, ranks * SQUARE_SIZE),
                             (files * SQUARE_SIZE, ranks * SQUARE_SIZE + SQUARE_SIZE), 2)
            pygame.draw.line(window, BLACK, (files * SQUARE_SIZE, ranks * SQUARE_SIZE),
                             (files * SQUARE_SIZE + SQUARE_SIZE, ranks * SQUARE_SIZE), 2)


# Renders all the pieces to its corresponding squares
def draw_pieces(board: chess.Board):
    for rank in range(RANKS):
        for file in range(FILES):
            square = rank * 8 + file
            piece = board.piece_at(square)
            if piece is not None:
                piece_name = f"{piece}{'w' if piece.color else 'b'}"
                draw_piece(piece_name, file, rank)


# Renders a single piece onto the pygame surface
def draw_piece(piece_name, file, rank):
    image = pygame.image.load("" + piece_name.lower() + ".png").convert_alpha()
    width = image.get_width() * PIECE_SIZE
    height = image.get_height() * PIECE_SIZE
    image = pygame.transform.scale(image, (width, height))
    window.blit(image, (file * SQUARE_SIZE, rank * SQUARE_SIZE))


# Forces an update of the screen
def update_screen():
    pygame.display.update()


if __name__ == '__main__':
    # Test GUI
    chess_board = chess.Board()
    while True:
        render_board(chess_board)
