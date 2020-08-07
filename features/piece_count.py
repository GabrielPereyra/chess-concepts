from functools import cached_property

import chess

from features.abstract import Features


# TODO: combine this with board?
class PieceCount(Features):
    def __init__(self, fen):
        self.board = chess.Board(fen)

    @cached_property
    def our_piece_count(self):
        return chess.popcount(self.board.occupied_co[self.board.turn])

    @cached_property
    def our_queens(self):
        return len(self.board.pieces(chess.QUEEN, self.board.turn))

    @cached_property
    def our_rooks(self):
        return len(self.board.pieces(chess.ROOK, self.board.turn))

    @cached_property
    def our_bishops(self):
        return len(self.board.pieces(chess.BISHOP, self.board.turn))

    @cached_property
    def our_knights(self):
        return len(self.board.pieces(chess.KNIGHT, self.board.turn))

    @cached_property
    def our_pawns(self):
        return len(self.board.pieces(chess.PAWN, self.board.turn))

    @cached_property
    def their_piece_count(self):
        return chess.popcount(self.board.occupied_co[not self.board.turn])

    @cached_property
    def their_queens(self):
        return len(self.board.pieces(chess.QUEEN, not self.board.turn))

    @cached_property
    def their_rooks(self):
        return len(self.board.pieces(chess.ROOK, not self.board.turn))

    @cached_property
    def their_bishops(self):
        return len(self.board.pieces(chess.BISHOP, not self.board.turn))

    @cached_property
    def their_knights(self):
        return len(self.board.pieces(chess.KNIGHT, not self.board.turn))

    @cached_property
    def their_pawns(self):
        return len(self.board.pieces(chess.PAWN, not self.board.turn))

    @cached_property
    def piece_count(self):
        return chess.popcount(self.board.occupied)

    @cached_property
    def material_advantage(self):
        return (
            self.our_queens * 9
            + self.our_rooks * 5
            + self.our_bishops * 3
            + self.our_knights * 3
            + self.our_pawns
            - self.their_queens * 9
            - self.their_rooks * 5
            - self.their_bishops * 3
            - self.their_knights * 3
            - self.their_pawns
        )
