from enum import IntEnum
from functools import cached_property

import chess

from features.abstract import Features
from features.motives import is_discovered_attack, is_skewer, is_sacrifice, is_pin
from features.helpers import is_greater_value


# TODO: consider refactoring to enum.IntFlag if we want them to behave like bit flags
# https://docs.python.org/3/library/enum.html#intflag
class Tactic(IntEnum):
    NONE = 0
    FORK = 1
    DISCOVERED_ATTACK = 2
    PIN = 3
    SKEWER = 4
    SACRIFICE = 5


class BestMove(Features):

    csvs = ["lichess", "stockfish10"]

    def __init__(self, fen, move):
        self.board = chess.Board(fen)
        self.move = chess.Move.from_uci(move)

    # TODO: replace this with an attribute which specifies columns
    @classmethod
    def from_row(cls, row):
        return cls(row.fen, row.best_move)

    @cached_property
    def best_move_piece_type(self):
        return self.board.piece_type_at(self.move.from_square)

    @cached_property
    def best_move_is_en_passant(self):
        return self.board.is_en_passant(self.move)

    @cached_property
    def best_move_is_promotion(self):
        return bool(self.move.promotion)

    @cached_property
    def best_move_is_capture(self):
        return self.board.is_capture(self.move)

    @cached_property
    def best_move_is_capture_higher_value(self):
        return is_greater_value(self.best_move_captures_piece_type, self.best_move_piece_type)

    @cached_property
    def best_move_gives_check(self):
        return self.board.gives_check(self.move)

    @cached_property
    def best_move_is_horizontal(self):
        from_rank = chess.square_rank(self.move.from_square)
        to_rank = chess.square_rank(self.move.to_square)
        return from_rank == to_rank

    @cached_property
    def best_move_is_forward(self):
        """From the perspective of the current player, i.e. current player's pawns move up the board."""
        from_rank = chess.square_rank(self.move.from_square)
        to_rank = chess.square_rank(self.move.to_square)
        if self.board.turn == chess.WHITE:
            return from_rank < to_rank
        return from_rank > to_rank

    @cached_property
    def best_move_is_backward(self):
        """From the perspective of the current player, i.e. current player's pawns move up the board."""
        return not self.best_move_is_horizontal and not self.best_move_is_forward

    @cached_property
    def best_move_from_square(self):
        return self.move.from_square

    @cached_property
    def best_move_to_square(self):
        return self.move.to_square

    @cached_property
    def best_move_was_defended(self):
        return self.board.is_attacked_by(self.board.turn, self.move.from_square)

    @cached_property
    def best_move_was_attacked(self):
        return self.board.is_attacked_by(not self.board.turn, self.move.from_square)

    @cached_property
    def best_move_was_hanging(self):
        return self.best_move_was_attacked and not self.best_move_was_defended

    @cached_property
    def best_move_captures_piece_type(self):
        if self.best_move_is_en_passant:
            return 1
        captures_piece_type = self.board.piece_type_at(self.move.to_square)
        return captures_piece_type if captures_piece_type else 0

    @cached_property
    def best_move_is_attacked(self):
        board = self.board.copy()
        board.push(self.move)
        return board.is_attacked_by(board.turn, self.move.to_square)

    @cached_property
    def best_move_is_defended(self):
        board = self.board.copy()
        board.push(self.move)
        return board.is_attacked_by(not board.turn, self.move.to_square)

    @cached_property
    def best_move_captures_hanging_piece(self):
        return self.best_move_is_capture and not self.best_move_is_attacked

    @cached_property
    def _best_move_pieces_attacked(self):
        board = self.board.copy()
        board.push(self.move)
        pieces_attacked_mask = board.attacks_mask(self.move.to_square)
        pieces_attacked_mask &= board.occupied_co[board.turn]
        return [
            board.piece_type_at(s) for s in chess.scan_reversed(pieces_attacked_mask)
        ]

    @cached_property
    def best_move_number_of_pieces_attacked(self):
        return len(self._best_move_pieces_attacked)

    @cached_property
    def best_move_number_of_higher_value_pieces_attacked(self):
        return sum(
            [
                is_greater_value(pt, self.best_move_piece_type)
                for pt in self._best_move_pieces_attacked
            ]
        )

    @cached_property
    def best_move_tactic(self):
        fen = self.board.fen()
        if is_sacrifice(fen, self.move):
            return Tactic.SACRIFICE
        if is_discovered_attack(fen, self.move):
            return Tactic.DISCOVERED_ATTACK
        if is_pin(fen, self.move):
            return Tactic.PIN
        if is_skewer(fen, self.move):
            return Tactic.SKEWER
        # TODO: uncomment lines below when is_fork(fen, move) is implemented
        # if is_fork(fen, self.move):
        #     return Tactic.FORK
        return Tactic.NONE
