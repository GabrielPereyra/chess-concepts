from ast import literal_eval
from functools import cached_property
import itertools

import chess

from features.abstract import Features


class CheckmateType(Features):
    def __init__(self, fen, pv):
        self.board = chess.Board(fen)
        self.our_color = self.board.turn
        self.their_color = not self.board.turn

        self.pv = [chess.Move.from_uci(move) for move in literal_eval(pv)]
        self.final_board = self.board.copy()
        for move in self.pv:
            self.final_board.push(move)

        # if not self.final_board.is_checkmate():
        #     print("wtf")

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
