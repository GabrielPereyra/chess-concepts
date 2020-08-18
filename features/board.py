from functools import cached_property

import chess

from features.abstract import Features
from features.helpers import count_material


class Board(Features):
    def __init__(self, fen):
        self.board = chess.Board(fen)
        self.moves = tuple(self.board.legal_moves)
        self.their_board = self.board.copy()
        self.their_board.push(chess.Move.null())
        self.their_moves = tuple(self.their_board.legal_moves)

    @cached_property
    def turn(self):
        return self.board.turn

    @cached_property
    def is_check(self):
        return self.board.is_check()

    @cached_property
    def fullmove_number(self):
        return self.board.fullmove_number

    @cached_property
    def our_number_of_moves(self):
        return len(self.moves)

    @cached_property
    def our_number_of_checks(self):
        count = 0
        for move in self.moves:
            self.board.push(move)
            count += self.board.is_check()
            self.board.pop()
        return count

    @cached_property
    def our_number_of_captures(self):
        count = 0
        for move in self.moves:
            count += self.board.is_capture(move)
        return count

    @cached_property
    def our_number_of_queen_moves(self):
        count = 0
        for move in self.moves:
            count += self.board.piece_type_at(move.from_square) == chess.QUEEN
        return count

    @cached_property
    def our_number_of_rook_moves(self):
        count = 0
        for move in self.moves:
            count += self.board.piece_type_at(move.from_square) == chess.ROOK
        return count

    @cached_property
    def our_number_of_bishop_moves(self):
        count = 0
        for move in self.moves:
            count += self.board.piece_type_at(move.from_square) == chess.BISHOP
        return count

    @cached_property
    def our_number_of_knight_moves(self):
        count = 0
        for move in self.moves:
            count += self.board.piece_type_at(move.from_square) == chess.KNIGHT
        return count

    @cached_property
    def our_number_of_pawn_moves(self):
        count = 0
        for move in self.moves:
            count += self.board.piece_type_at(move.from_square) == chess.PAWN
        return count

    @cached_property
    def their_number_of_moves(self):
        return len(self.their_moves)

    @cached_property
    def their_number_of_checks(self):
        count = 0
        for move in self.their_moves:
            self.their_board.push(move)
            count += self.their_board.is_check()
            self.their_board.pop()
        return count

    @cached_property
    def their_number_of_captures(self):
        count = 0
        for move in self.their_moves:
            count += self.their_board.is_capture(move)
        return count

    @cached_property
    def their_number_of_queen_moves(self):
        count = 0
        for move in self.their_moves:
            count += self.their_board.piece_type_at(move.from_square) == chess.QUEEN
        return count

    @cached_property
    def their_number_of_rook_moves(self):
        count = 0
        for move in self.their_moves:
            count += self.their_board.piece_type_at(move.from_square) == chess.ROOK
        return count

    @cached_property
    def their_number_of_bishop_moves(self):
        count = 0
        for move in self.their_moves:
            count += self.their_board.piece_type_at(move.from_square) == chess.BISHOP
        return count

    @cached_property
    def their_number_of_knight_moves(self):
        count = 0
        for move in self.their_moves:
            count += self.their_board.piece_type_at(move.from_square) == chess.KNIGHT
        return count

    @cached_property
    def their_number_of_pawn_moves(self):
        count = 0
        for move in self.their_moves:
            count += self.their_board.piece_type_at(move.from_square) == chess.PAWN
        return count

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
    def our_non_pawn_pieces(self):
        return self.our_piece_count - self.our_pawns

    @cached_property
    def our_majors(self):
        return self.our_queens + self.our_rooks

    @cached_property
    def our_minors(self):
        return self.our_bishops + self.our_knights

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
    def their_non_pawn_pieces(self):
        return self.their_piece_count - self.their_pawns

    @cached_property
    def their_majors(self):
        return self.their_queens + self.their_rooks

    @cached_property
    def their_minors(self):
        return self.their_bishops + self.their_knights

    @cached_property
    def piece_count(self):
        return chess.popcount(self.board.occupied)

    @cached_property
    def our_material_count(self):
        return count_material(self.board, self.turn)

    @cached_property
    def their_material_count(self):
        return count_material(self.board, not self.turn)

    @cached_property
    def material_count(self):
        return self.our_material_count + self.their_material_count

    @cached_property
    def material_advantage(self):
        return self.our_material_count - self.their_material_count

    @cached_property
    def phase(self):
        if self.fullmove_number < 15:
            return 0 # opening
        elif self.material_count < 39:
            return 1 # endgame
        else:
            return 2 # midgame

    @cached_property
    def endgame_type(self):
        if (self.our_non_pawn_pieces == 0 and self.their_non_pawn_pieces == 0):
            return 0 # pawn endgame
        if (self.our_majors == 0 and self.their_majors == 0):
            return 1 # minors and pawns
        if (self.our_minors == 0 and self.their_minors == 0):
            return 2 # majors and pawns
        if (
            self.our_rooks == 0 and
            self.our_minors == 0 and
            self.their_rooks == 0 and
            self.their_minors == 0
        ):
            return 3 # queens and pawns
        if (
            self.our_queens == 0 and
            self.our_minors == 0 and
            self.their_queens == 0 and
            self.their_minors == 0
        ):
            return 4 # rooks and pawns
        if (
            self.our_majors == 0 and
            self.our_knights == 0 and
            self.their_majors == 0 and
            self.their_knights == 0
        ):
            return 5 # bishops and pawns
        if (
            self.our_majors == 0 and
            self.our_bishops == 0 and
            self.their_majors == 0 and
            self.their_bishops == 0
        ):
            return 6 # knights and pawns