from functools import cached_property

import chess
from chess import PAWN, KNIGHT, BISHOP, ROOK, QUEEN
from features.abstract import Features
from features.helpers import is_greater_value


import pandas as pd


OURS, THEIRS = True, False


def squares_to_piece_types(board, squares):
    return [board.piece_type_at(square) for square in squares]


class Piece():

    def __init__(self, board, square):
        self.square = square
        piece = board.piece_at(square)
        self.piece_type = piece.piece_type
        self.color = piece.color

        # self.is_attacked = board.is_attacked_by(not self.color, square)
        # self.is_defended = board.is_attacked_by(self.color, square)
        # self.is_hanging = self.is_attacked and not self.is_defended
        # self.is_pinned = board.is_pinned(self.color, square)

        attackers = board.attackers(not self.color, square)
        # defenders = board.attackers(self.color, square)
        self.piece_types_attacking = squares_to_piece_types(board, attackers)
        # self.piece_types_defending = squares_to_piece_types(board, defenders)

        # attacks = board.attacks(square)
        # self.piece_types_attacked = squares_to_piece_types(board, attacks)

        self.is_attacked_by_lower_value = any([is_greater_value(self.piece_type, pt) for pt in self.piece_types_attacking])

    def as_row(self):
        # TODO: get this from __dict___
        return {
            'piece_type': self.piece_type,
            'color': self.color,

            # 'is_attacked': self.is_attacked,
            # 'is_defended': self.is_defended,
            # 'is_hanging': self.is_hanging,
            # 'is_pinned': self.is_pinned,
            #
            # 'piece_types_attacking': self.piece_types_attacking,
            # 'piece_types_defending': self.piece_types_defending,
            # 'piece_types_attacked': self.piece_types_attacked,

            'is_attacked_by_lower_value': self.is_attacked_by_lower_value
        }


class Threats(Features):

    def __init__(self, fen):
        board = chess.Board(fen)
        pieces = [Piece(board, s) for s in chess.scan_reversed(board.occupied)]
        rows = [p.as_row() for p in pieces]
        self.df = pd.DataFrame(rows)
        self.turn = board.turn

    @cached_property
    def _our_df(self):
        return self.df[self.df['color'] == self.turn]

    @cached_property
    def _their_df(self):
        return self.df[self.df['color'] != self.turn]
    #
    # @cached_property
    # def our_pinned_pieces(self):
    #     return len(self._our_df[self._our_df['is_pinned']])
    #
    # @cached_property
    # def their_pinned_pieces(self):
    #     return len(self._their_df[self._their_df['is_pinned']])

    @cached_property
    def our_pieces_attacked_by_lower_value(self):
        return len(self._our_df[self._our_df['is_attacked_by_lower_value']])

    @cached_property
    def their_pieces_attacked_by_lower_value(self):
        return len(self._their_df[self._their_df['is_attacked_by_lower_value']])

    # @cached_property
    # def our_pieces_attacked(self):
    #     return len(self._our_df[self._our_df['is_attacked']])
    #
    # @cached_property
    # def their_pieces_attacked(self):
    #     return len(self._their_df[self._their_df['is_attacked']])
    #
    # @cached_property
    # def our_pieces_defended(self):
    #     return len(self._our_df[self._our_df['is_defended']])
    #
    # @cached_property
    # def their_pieces_defended(self):
    #     return len(self._their_df[self._their_df['is_defended']])
    #
    # @cached_property
    # def our_pieces_hanging(self):
    #     return len(self._our_df[self._our_df['is_hanging']])
    #
    # @cached_property
    # def their_pieces_hanging(self):
    #     return len(self._their_df[self._their_df['is_hanging']])


class ThreatsAfterBestMove(Features):

    csvs = ["lichess", "stockfish10"]

    def __init__(self, fen, move):
        board = chess.Board(fen)
        self.turn = board.turn
        board.push(chess.Move.from_uci(move))
        pieces = [Piece(board, s) for s in chess.scan_reversed(board.occupied)]
        rows = [p.as_row() for p in pieces]
        self.df = pd.DataFrame(rows)

    # TODO: replace this with an attribute which specifies columns
    @classmethod
    def from_row(cls, row):
        return cls(row.fen, row.best_move)

    @cached_property
    def _our_df(self):
        return self.df[self.df['color'] == self.turn]

    @cached_property
    def _their_df(self):
        return self.df[self.df['color'] != self.turn]

    @cached_property
    def our_pieces_attacked_by_lower_value_after_best_move(self):
        return len(self._our_df[self._our_df['is_attacked_by_lower_value']])

    @cached_property
    def their_pieces_attacked_by_lower_value_after_best_move(self):
        return len(self._their_df[self._their_df['is_attacked_by_lower_value']])


if __name__ == '__main__':
    board = chess.Board(None)
    board.set_piece_at(chess.A2, chess.Piece(PAWN, chess.WHITE))
    board.set_piece_at(chess.B3, chess.Piece(KNIGHT, chess.BLACK))

    pieces = Threats(board.fen())

    import pdb; pdb.set_trace()
