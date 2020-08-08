from functools import cached_property

import chess

from features.abstract import Features


class Checkmate(Features):

    csvs = ["lichess", "stockfish10"]

    def __init__(self, fen, pv):
        self.board = chess.Board(fen)
        self.our_color = self.board.turn
        self.their_color = not self.board.turn

        self.pv = [chess.Move.from_uci(move) for move in eval(pv)]
        for move in self.pv:
            self.board.push(move)

        # TODO: need to figure out why this happens.
        if not self.board.is_checkmate():
            print("wtf")

    @classmethod
    def from_row(cls, row):
        return cls(row.fen, row.best_pv)

    @cached_property
    def _their_king_ring_mask(self):
        their_king = self.board.king(self.their_color)
        return self.board.attacks_mask(their_king)

    @cached_property
    def _their_king_ring_and_king_mask(self):
        their_king_mask = self.board.occupied_co[self.their_color] & self.board.kings
        return their_king_mask | self._their_king_ring_mask

    @cached_property
    def num_our_pieces_attacking_their_king_ring(self):
        count = 0
        for piece in chess.scan_reversed(self.board.occupied_co[self.our_color]):
            piece_attacks_mask = self.board.attacks_mask(piece)
            count += bool(self._their_king_ring_and_king_mask & piece_attacks_mask)
        return count

    @cached_property
    def our_king_is_attacking_their_king_and_ring(self):
        our_king = self.board.king(self.our_color)
        their_king = self.board.king(self.their_color)
        return chess.square_distance(our_king, their_king) == 2

    @cached_property
    def num_our_queens_attacking_their_king_and_ring(self):
        count = 0
        for piece in self.board.pieces(chess.QUEEN, self.our_color):
            piece_attacks_mask = self.board.attacks_mask(piece)
            count += bool(self._their_king_ring_and_king_mask & piece_attacks_mask)
        return count

    @cached_property
    def num_our_rooks_attacking_their_king_and_ring(self):
        count = 0
        for piece in self.board.pieces(chess.ROOK, self.our_color):
            piece_attacks_mask = self.board.attacks_mask(piece)
            count += bool(self._their_king_ring_and_king_mask & piece_attacks_mask)
        return count

    @cached_property
    def num_our_bishops_attacking_their_king_and_ring(self):
        count = 0
        for piece in self.board.pieces(chess.BISHOP, self.our_color):
            piece_attacks_mask = self.board.attacks_mask(piece)
            count += bool(self._their_king_ring_and_king_mask & piece_attacks_mask)
        return count

    @cached_property
    def num_our_knights_attacking_their_king_and_ring(self):
        count = 0
        for piece in self.board.pieces(chess.KNIGHT, self.our_color):
            piece_attacks_mask = self.board.attacks_mask(piece)
            count += bool(self._their_king_ring_and_king_mask & piece_attacks_mask)
        return count

    @cached_property
    def num_our_pawns_attacking_their_king_and_ring(self):
        count = 0
        for piece in self.board.pieces(chess.PAWN, self.our_color):
            piece_attacks_mask = self.board.attacks_mask(piece)
            count += bool(self._their_king_ring_and_king_mask & piece_attacks_mask)
        return count

    @cached_property
    def checkmate_piece_type(self):
        move = self.pv[-1]
        return self.board.piece_type_at(move.to_square)

    @cached_property
    def checkmate_move_rank(self):
        board = self.board.copy()
        if board.turn == chess.BLACK:
            board = board.mirror()
        return chess.square_rank(self.pv[-1].to_square)

    @cached_property
    def their_king_rank(self):
        board = self.board.copy()
        if not board.turn:
            board = board.mirror()
        return chess.square_rank(board.king(not board.turn))

    @cached_property
    def their_king_file(self):
        board = self.board.copy()
        if not board.turn:
            board = board.mirror()
        return chess.square_file(board.king(not board.turn))

    @cached_property
    def their_king_is_back_rank(self):
        return self.their_king_rank == 7

    @cached_property
    def their_num_pieces_in_king_ring(self):
        their_pieces_mask = self.board.occupied_co[self.their_color]
        return chess.popcount(self._their_king_ring_mask & their_pieces_mask)

    @cached_property
    def our_num_pieces_in_king_ring(self):
        our_pieces_mask = self.board.occupied_co[self.our_color]
        return chess.popcount(self._their_king_ring_mask & our_pieces_mask)

    @cached_property
    def their_king_ring_size(self):
        return chess.popcount(self._their_king_ring_mask)

    @cached_property
    def is_box_mate(self):
        return (
            self.our_king_is_attacking_their_king_and_ring
            and self.num_our_pieces_attacking_their_king_ring == 2
        )
