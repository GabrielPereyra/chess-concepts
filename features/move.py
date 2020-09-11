from functools import cached_property

import chess

from board import AugBoard
from features.abstract import Features
from features.helpers import is_greater_value


class Move(Features):

    csvs = ["lichess", "stockfish10"]

    def __init__(self, fen, move):
        self.aug = AugBoard(fen)
        self.move = chess.Move.from_uci(move)

    @cached_property
    def piece_type(self):
        return self.aug.piece_type_at(self.move.from_square)

    @cached_property
    def is_en_passant(self):
        return self.aug.is_en_passant(self.move)

    @cached_property
    def is_castling(self):
        return self.aug.is_castling(self.move)

    @cached_property
    def is_underpromotion(self):
        return self.aug.is_underpromotion(self.move)

    @cached_property
    def is_promotion(self):
        return bool(self.move.promotion)

    @cached_property
    def is_capture(self):
        return self.aug.is_capture(self.move)

    @cached_property
    def is_capture_higher_value(self):
        return is_greater_value(self.captures_piece_type, self.piece_type)

    @cached_property
    def gives_check(self):
        return self.aug.gives_check(self.move)

    @cached_property
    def is_horizontal(self):
        from_rank = chess.square_rank(self.move.from_square)
        to_rank = chess.square_rank(self.move.to_square)
        return from_rank == to_rank

    @cached_property
    def is_forward(self):
        """From the perspective of the current player, i.e. current player's pawns move up the board."""
        from_rank = chess.square_rank(self.move.from_square)
        to_rank = chess.square_rank(self.move.to_square)
        if self.aug.current_color == chess.WHITE:
            return from_rank < to_rank
        return from_rank > to_rank

    @cached_property
    def is_backward(self):
        """From the perspective of the current player, i.e. current player's pawns move up the board."""
        return not self.is_horizontal and not self.is_forward

    @cached_property
    def from_square(self):
        return self.move.from_square

    @cached_property
    def to_square(self):
        return self.move.to_square

    @cached_property
    def was_defended(self):
        return self.aug.is_attacked_by(self.aug.current_color, self.move.from_square)

    @cached_property
    def was_attacked(self):
        return self.aug.is_attacked_by(self.aug.other_color, self.move.from_square)

    @cached_property
    def was_hanging(self):
        return self.was_attacked and not self.was_defended

    @cached_property
    def captures_piece_type(self):
        if self.is_en_passant:
            return 1
        captures_piece_type = self.aug.piece_type_at(self.move.to_square)
        return captures_piece_type if captures_piece_type else 0

    @cached_property
    def is_attacked(self):
        board = self.aug.copy()
        board.push(self.move)
        return board.is_attacked_by(board.current_color, self.move.to_square)

    @cached_property
    def is_defended(self):
        board = self.aug.copy()
        board.push(self.move)
        return board.is_attacked_by(board.other_color, self.move.to_square)

    @cached_property
    def captures_hanging_piece(self):
        return self.is_capture and not self.is_attacked

    @cached_property
    def _pieces_attacked(self):
        board = self.aug.copy()
        board.push(self.move)
        pieces_attacked_mask = board.attacks_mask(self.move.to_square)
        pieces_attacked_mask &= board.occupied_co(board.current_color)
        return [
            board.piece_type_at(s) for s in chess.scan_reversed(pieces_attacked_mask)
        ]

    @cached_property
    def number_of_pieces_attacked(self):
        return len(self._pieces_attacked)

    @cached_property
    def number_of_higher_value_pieces_attacked(self):
        return sum(
            [is_greater_value(pt, self.piece_type) for pt in self._pieces_attacked]
        )

    def _tactics(self):
        return self.aug.move_tactics(self.move)

    # TODO: consider changing return type so it can handle multiple tactics
    @cached_property
    def tactic(self):
        return self._tactics()[0]

    def _threats(self):
        return self.aug.move_threats(self.move)

    # TODO: consider changing return type so it can handle multiple tactics
    @cached_property
    def threat(self):
        return self._threats()[0]
