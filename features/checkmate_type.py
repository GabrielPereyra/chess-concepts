from ast import literal_eval
from functools import cached_property
import itertools

import chess

from features.abstract import Features


def non_empty_powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(1, len(s) + 1)
    )


def generate_mates_with_moved_piece_types_features(cls):
    for piece_types in non_empty_powerset(chess.PIECE_TYPES):
        name = "mate_with_moved_{}".format(
            "_".join([chess.piece_name(piece_type) for piece_type in piece_types])
        )

        def make_f(piece_types):
            def f(self):
                return self._mate_with_moved_piece_types(piece_types)

            return f

        f = make_f(piece_types)

        cached_f = cached_property(f)
        cached_f.__set_name__(None, name)
        setattr(cls, name, cached_f)
    return cls


@generate_mates_with_moved_piece_types_features
class CheckmateType(Features):
    def __init__(self, fen, pv):
        self.board = chess.Board(fen)
        self.our_color = self.board.turn
        self.their_color = not self.board.turn

        self.pv = [chess.Move.from_uci(move) for move in literal_eval(pv)]
        self.final_board = self.board.copy()
        for move in self.pv:
            self.final_board.push(move)

        if not self.final_board.is_checkmate():
            print("wtf")

    @classmethod
    def from_row(cls, row):
        return cls(row.fen, row.best_pv)

    @cached_property
    def is_back_rank_mate(self):
        """
        According to Wikipedia:
        > In chess, a back-rank checkmate (also known as the corridor mate) is a checkmate delivered by a rook or queen
        > along a back rank (that is, the row on which the pieces [not pawns] stand at the start of the game) in which
        > the mated king is unable to move up the board because the king is blocked by friendly pieces (usually pawns)
        > on the second rank.
        source: https://en.wikipedia.org/wiki/Back-rank_checkmate
        """

        """
        conditions:
        - their king is on their back rank
        - last moved piece was either queen or rook
        - last moved piece was moved to their back rank
        - all squares their king attacks that are not on their back rank are occupied by their pieces
        """

        their_back_rank = 7 if self.their_color == chess.BLACK else 0

        their_king = self.final_board.king(self.their_color)
        if chess.square_rank(their_king) != their_back_rank:
            return False

        last_move = self.pv[-1]

        if chess.square_rank(last_move.to_square) != their_back_rank:
            return False

        if self.final_board.piece_type_at(last_move.to_square) not in [
            chess.QUEEN,
            chess.ROOK,
        ]:
            return False

        for square in self.final_board.attacks(their_king):
            if chess.square_rank(square) == their_back_rank:
                continue
            piece = self.final_board.piece_at(square)
            if piece is None or piece.color != self.their_color:
                return False
        return True

    @cached_property
    def is_smothered_mate(self):
        """
        According to Wikipedia:
        > In chess, a smothered mate is a checkmate delivered by a knight in which the mated king is unable to move
        > because he is surrounded (or smothered) by his own pieces.
        source: https://en.wikipedia.org/wiki/Smothered_mate
        """

        their_king = self.final_board.king(self.their_color)
        for square in self.final_board.attacks(their_king):
            piece = self.final_board.piece_at(square)
            if piece is None or piece.color != self.their_color:
                return False
        return True

    def _mate_with_moved_piece_types(self, piece_types):
        board = self.board.copy()
        our_moved_piece_types = set()
        for move in self.pv:
            board.push(move)
            piece = board.piece_at(move.to_square)
            if piece.color == self.our_color:
                our_moved_piece_types.add(piece.piece_type)
        return set(piece_types) == our_moved_piece_types
