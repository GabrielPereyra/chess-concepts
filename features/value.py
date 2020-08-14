from functools import cached_property

import chess

from features.abstract import Features
from features.helpers import is_higher_value


def is_attacked_by_lower_value(board, color, square):
    piece_type = board.piece_type_at(square)
    for attacker in board.attackers(color, square):
        attacker_piece_type = board.piece_type_at(attacker)
        if is_higher_value(piece_type, attacker_piece_type):
            return True
    return False


# TODO: how to merge all of these?
def attacks_on_higher_value_pieces(board, color):
    pieces_mask = board.occupied_co[not color]

    attacks_on_higher_value_pieces = 0
    for square in chess.scan_forward(pieces_mask):
        attacks_on_higher_value_pieces += is_attacked_by_lower_value(
            board, color, square
        )

    return attacks_on_higher_value_pieces


def hanging_pieces(board, color):
    pieces = board.occupied_co[color]
    hanging_pieces = 0
    for piece in chess.scan_forward(pieces):
        is_attacked = board.is_attacked_by(not color, piece)
        is_defended = board.is_attacked_by(color, piece)
        hanging_pieces += is_attacked and not is_defended
    return hanging_pieces


def is_attacked_by_piece_type(board, color, square, piece_type):
    for attacker in board.attackers(color, square):
        if board.piece_type_at(attacker) == piece_type:
            return True
    return False


def weak_pieces(board, color):
    """Attacked pieces not defended by a pawn."""
    pieces = board.occupied_co[color]
    weak_pieces = 0
    for piece in chess.scan_forward(pieces):
        is_attacked = board.is_attacked_by(not color, piece)
        is_defended_by_pawn = is_attacked_by_piece_type(
            board, color, piece, chess.PAWN,
        )
        weak_pieces += is_attacked and not is_defended_by_pawn
    return weak_pieces


# TODO: add stockfish eval function features...
class Value(Features):
    """Features should be correlated with stockfish score evaluation."""

    def __init__(self, fen):
        self.board = chess.Board(fen)

    @cached_property
    def our_hanging_pieces(self):
        return hanging_pieces(self.board, self.board.turn)

    @cached_property
    def their_hanging_pieces(self):
        return hanging_pieces(self.board, not self.board.turn)

    @cached_property
    def our_weak_pieces(self):
        return weak_pieces(self.board, self.board.turn)

    @cached_property
    def their_weak_pieces(self):
        return weak_pieces(self.board, not self.board.turn)

    # TODO: control?

    # @cached_property
    # def our_attacks_on_higher_value_pieces(self):
    #     return attacks_on_higher_value_pieces(self.board, self.board.turn)
    #
    # @cached_property
    # def their_attacks_on_higher_value_pieces(self):
    #     return attacks_on_higher_value_pieces(self.board, not self.board.turn)
