from typing import List

import chess.pgn
import random

from chess import WHITE, BLACK


# This file is deprecated
# It was used to help create and generate training data using the FEN (Forsyth-Edwards-Notation) -
# a system to write board positions using a maximum of 80 and an average of 40 characters
def get_random_fen_from_games(games: List[chess.pgn.Game]):
    board = chess.Board()
    game = random.choice(games)
    move_count = int(game.headers["PlyCount"]) / 2
    chosen_move = int(random.random() * move_count)

    i = 0
    for move in game.mainline_moves():
        board.push(move)
        if board.turn == WHITE:
            if i >= chosen_move:
                return board.fen()
            i += 1


piece_list = ["R", "N", "B", "Q", "P"]


def get_random_fen():
    board = [[" " for _ in range(8)] for _ in range(8)]
    piece_amount_white, piece_amount_black = random.randint(0, 15), random.randint(0, 15)
    place_kings(board)
    populate_board(board, piece_amount_white, piece_amount_black)
    return fen_from_board(board)


def place_kings(brd):
    while True:
        rank_white, file_white, rank_black, file_black = random.randint(0, 7), random.randint(0, 7), random.randint(0,
                                                                                                                    7), random.randint(
            0, 7)
        diff_list = [abs(rank_white - rank_black), abs(file_white - file_black)]
        if sum(diff_list) > 2 or set(diff_list) == set([0, 2]):
            brd[rank_white][file_white], brd[rank_black][file_black] = "K", "k"
            break


def populate_board(brd, wp, bp):
    for x in range(2):
        if x == 0:
            piece_amount = wp
            pieces = piece_list
        else:
            piece_amount = bp
            pieces = [s.lower() for s in piece_list]
        while piece_amount != 0:
            piece_rank, piece_file = random.randint(0, 7), random.randint(0, 7)
            piece = random.choice(pieces)
            if brd[piece_rank][piece_file] == " " and pawn_on_promotion_square(piece, piece_rank) == False:
                brd[piece_rank][piece_file] = piece
                piece_amount -= 1


def fen_from_board(brd):
    fen = ""
    for x in brd:
        n = 0
        for y in x:
            if y == " ":
                n += 1
            else:
                if n != 0:
                    fen += str(n)
                fen += y
                n = 0
        if n != 0:
            fen += str(n)
        fen += "/" if fen.count("/") < 7 else ""
    fen += " w - - 0 1\n"
    return fen


def pawn_on_promotion_square(pc, pr):
    if pc == "P" and pr == 0:
        return True
    elif pc == "p" and pr == 7:
        return True
    return False
