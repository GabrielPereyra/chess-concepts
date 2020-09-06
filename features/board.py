from enum import IntEnum
from functools import cached_property

import chess

import board
from features.abstract import Features


class GamePhase(IntEnum):
    OPENING = 0
    MIDDLEGAME = 1
    ENDGAME = 2


class PositionOpenness(IntEnum):
    OPEN = 0
    SEMI_OPEN = 1
    CLOSED = 2


class Board(Features):
    def __init__(self, fen):
        self.board = board.AugBoard(fen)
        self.moves = tuple(self.board.legal_moves)
        self.their_board = self.board.copy()
        self.their_board.push(chess.Move.null())
        self.their_moves = tuple(self.their_board.legal_moves)

    @cached_property
    def turn(self):
        return self.board.current_color

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
        return chess.popcount(self.board.occupied_co(self.board.current_color))

    @cached_property
    def our_queens(self):
        return len(self.board.pieces(chess.QUEEN, self.board.current_color))

    @cached_property
    def our_rooks(self):
        return len(self.board.pieces(chess.ROOK, self.board.current_color))

    @cached_property
    def our_bishops(self):
        return len(self.board.pieces(chess.BISHOP, self.board.current_color))

    @cached_property
    def our_knights(self):
        return len(self.board.pieces(chess.KNIGHT, self.board.current_color))

    @cached_property
    def our_pawns(self):
        return len(self.board.pieces(chess.PAWN, self.board.current_color))

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
    def our_bishop_pair(self):
        return self.our_bishops >= 2 and self.their_bishops <= 1

    @cached_property
    def their_piece_count(self):
        return chess.popcount(self.board.occupied_co(self.board.other_color))

    @cached_property
    def their_queens(self):
        return len(self.board.pieces(chess.QUEEN, self.board.other_color))

    @cached_property
    def their_rooks(self):
        return len(self.board.pieces(chess.ROOK, self.board.other_color))

    @cached_property
    def their_bishops(self):
        return len(self.board.pieces(chess.BISHOP, self.board.other_color))

    @cached_property
    def their_knights(self):
        return len(self.board.pieces(chess.KNIGHT, self.board.other_color))

    @cached_property
    def their_pawns(self):
        return len(self.board.pieces(chess.PAWN, self.board.other_color))

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
    def their_bishop_pair(self):
        return self.their_bishops >= 2 and self.our_bishops <= 1

    @cached_property
    def piece_count(self):
        return chess.popcount(self.board.occupied)

    @cached_property
    def our_material_count(self):
        return self.board.count_material(self.board.current_color)

    @cached_property
    def their_material_count(self):
        return self.board.count_material(self.board.other_color)

    @cached_property
    def material_count(self):
        return self.our_material_count + self.their_material_count

    @cached_property
    def material_advantage(self):
        return self.our_material_count - self.their_material_count

    @staticmethod
    def _locked_pawns(fen):
        """
        A pawn is locked iff. it cannot move forward because opponent's pawn occupy the square in front and cannot move
        diagonally, i.e. make a capture, because no such capture is available, regardless of whose turn is it.
        """

        board = chess.Board(fen)
        board_opposite_turn = board.copy()
        board_opposite_turn.turn = not board.turn

        locked_pawns = set()
        for square in chess.scan_forward(board.pawns):
            color = board.piece_at(square).color
            square_in_front = square + 8 if color == chess.WHITE else square - 8
            if not (0 <= square_in_front < 64):
                continue
            piece_in_front = board.piece_at(square_in_front)
            from_mask = chess.BB_SQUARES[square]
            if (
                piece_in_front is not None
                and piece_in_front.piece_type == chess.PAWN
                and piece_in_front.color != color
                and not list(board.generate_legal_captures(from_mask))
                and not list(board_opposite_turn.generate_legal_captures(from_mask))
            ):
                locked_pawns.add(square)
        return locked_pawns

    @cached_property
    def position_openness(self):
        """
        Open:
        An open position is defined as a position with no locked pawns and typically 3 or more pawns have been traded.
        source: https://www.ichess.net/blog/three-types-positions-open/

        Semi-open:
        > A semi-open position is defined as a position with very few or no locked pawns and typically 1 or 2 pawns may
        > have been traded.
        source: https://www.ichess.net/blog/three-types-positions-semi-open/

        Closed:
        A closed position is defined as a position with a locked pawn center and typically very few (if any) pawns have
        been traded.
        source: https://www.ichess.net/blog/three-types-positions-closed/
        """

        locked_pawns = self._locked_pawns(self.board.fen())
        center_files = "cdef"
        locked_center_pawns = {
            square
            for square in locked_pawns
            if chess.FILE_NAMES[chess.square_file(square)] in center_files
        }
        num_locked_center_pawns = len(locked_center_pawns)
        num_traded_pawns = 16 - (self.our_pawns + self.their_pawns)
        if num_locked_center_pawns == 0 and num_traded_pawns >= 5:
            return PositionOpenness.OPEN
        if num_locked_center_pawns <= 2 and num_traded_pawns >= 2:
            return PositionOpenness.SEMI_OPEN
        return PositionOpenness.CLOSED

    def _non_pawn_pieces_on_origin_squares(self, color: chess.Color):
        origins = {
            chess.A1: chess.ROOK,
            chess.B1: chess.KNIGHT,
            chess.C1: chess.BISHOP,
            chess.D1: chess.QUEEN,
            chess.E1: chess.KING,
            chess.F1: chess.BISHOP,
            chess.G1: chess.KNIGHT,
            chess.H1: chess.KNIGHT,
        }
        piece_types = []
        for square, expected in origins.items():
            if color == chess.BLACK:
                square = chess.square_mirror(square)
            piece_type = self.board.piece_type_at(square)
            if piece_type == expected:
                piece_types.append(piece_type)
        return piece_types

    @cached_property
    def phase(self):
        our_pieces_on_origin_squares = self._non_pawn_pieces_on_origin_squares(
            self.turn
        )
        their_pieces_on_origin_squares = self._non_pawn_pieces_on_origin_squares(
            not self.turn
        )

        def is_endgame_phase(num_non_pawn_pieces, num_queens, pieces_on_origin_squares):
            return num_non_pawn_pieces <= 4 or (
                num_non_pawn_pieces == 5
                and num_queens == 0
                and len(pieces_on_origin_squares) <= 2
            )

        our_endgame_phase = is_endgame_phase(
            self.our_non_pawn_pieces,
            self.our_queens,
            self._non_pawn_pieces_on_origin_squares(self.turn),
        )
        their_endgame_phase = is_endgame_phase(
            self.their_non_pawn_pieces,
            self.their_queens,
            self._non_pawn_pieces_on_origin_squares(not self.turn),
        )
        if our_endgame_phase and their_endgame_phase:
            return GamePhase.ENDGAME

        if (
            min(len(our_pieces_on_origin_squares), len(their_pieces_on_origin_squares))
            <= 2
        ):
            return GamePhase.MIDDLEGAME
        return GamePhase.OPENING

    @cached_property
    def endgame_type(self):
        if self.our_non_pawn_pieces == 0 and self.their_non_pawn_pieces == 0:
            return 0  # pawn endgame
        if self.our_majors == 0 and self.their_majors == 0:
            return 1  # minors and pawns
        if self.our_minors == 0 and self.their_minors == 0:
            return 2  # majors and pawns
        if (
            self.our_rooks == 0
            and self.our_minors == 0
            and self.their_rooks == 0
            and self.their_minors == 0
        ):
            return 3  # queens and pawns
        if (
            self.our_queens == 0
            and self.our_minors == 0
            and self.their_queens == 0
            and self.their_minors == 0
        ):
            return 4  # rooks and pawns
        if (
            self.our_majors == 0
            and self.our_knights == 0
            and self.their_majors == 0
            and self.their_knights == 0
        ):
            return 5  # bishops and pawns
        if (
            self.our_majors == 0
            and self.our_bishops == 0
            and self.their_majors == 0
            and self.their_bishops == 0
        ):
            return 6  # knights and pawns

    @cached_property
    def pawn_structure(self):
        return self.board.pawn_structure()
