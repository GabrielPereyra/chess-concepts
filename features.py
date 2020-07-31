import click
import chess
import chess.engine
import pandas as pd
from functools import cached_property
STOCKFISH_PATH = '../Stockfish/src/stockfish'


# TODO: queen support by a piece
# TODO: single piece (number of pieces involved)
# TODO: best move is safe check
# TODO: best move is capture hanging

# TODO: best move is sacrifice

# TODO: battery (queen support by bishop, rook in king ring.)

# TODO: is back rank mate (only attacked by queen or rook)

def _is_feature(attr):
    return (
        not attr.startswith('__') and
        not attr.startswith('_') and
        attr not in ['features', 'feature_names', 'from_row', 'from_df']
    )


# TODO: make this inherit from dict?
class Features:

    @classmethod
    def feature_names(cls):
        return [attr for attr in dir(cls) if _is_feature(attr)]

    def features(self):
        feature_dict = {}
        for feature_name in self.feature_names():
                feature_dict[feature_name] = getattr(self, feature_name)
        return feature_dict

    # TODO: how to handle tuple and row? dict on tuple?
    @classmethod
    def from_row(cls, row):
        return cls(row.fen)

    @classmethod
    def from_df(cls, df):
        # TODO: put click in here...
        feature_rows = []
        with click.progressbar(tuple(df.itertuples())) as rows:
            for row in rows:
                feature_instance = cls.from_row(row)
                feature_rows.append(feature_instance.features())
        return pd.DataFrame(feature_rows)


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

    # TODO: redundent with number of pieces attacked.
    @cached_property
    def our_number_of_captures(self):
        count = 0
        for move in self.moves:
            count += self.board.is_capture(move)
        return count

    # TODO: probably move this to pieces?
    # TODO: this is different than attack mask...
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
            self.our_queens * 8 +
            self.our_rooks * 5 +
            self.our_bishops * 3 +
            self.our_knights * 3 +
            self.our_pawns -
            self.their_queens * 8 -
            self.their_rooks * 5 -
            self.their_bishops * 3 -
            self.their_knights * 3 -
            self.their_pawns
        )


class BestMove(Features):

    def __init__(self, fen, move):
        self.board = chess.Board(fen)
        self.move = chess.Move.from_uci(move)

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
    def best_move_is_check(self):
        self.board.push(self.move)
        is_check = self.board.is_check()
        self.board.pop()
        return is_check

    # TODO: this are incorrect - push move and then check.
    @cached_property
    def best_move_is_defended(self):
        return self.board.is_attacked_by(self.board.turn, self.move.to_square)

    @cached_property
    def best_move_is_attacked(self):
        return self.board.is_attacked_by(not self.board.turn, self.move.to_square)

    # @cached_property
    # def best_move_was_defended(self):
    #     return self.board.is_attacked_by(self.board.turn, self.move.from_square)
    #
    # @cached_property
    # def best_move_was_attacked(self):
    #     return self.board.is_attacked_by(not self.board.turn, self.move.from_square)
    #
    # @cached_property
    # def best_move_was_hanging(self):
    #     return self.best_move_was_attacked and not self.best_move_was_defended
    #
    #
    # @cached_property
    # def best_move_captures_piece_type(self):
    #     if self.best_move_is_en_passant: return 1
    #     captures_piece_type = self.board.piece_type_at(self.move.to_square)
    #     return captures_piece_type if captures_piece_type else 0
    #
    # @cached_property
    # def best_move_captures_hanging_piece(self):
    #     return self.best_move_is_capture and not self.best_move_is_attacked
    #
    # @cached_property
    # def best_move_captures_higher_value_piece(self):
    #     piece_to_value = list(range(7))
    #     piece_to_value[2] = 3
    #     if self.best_move_is_capture:
    #         return piece_to_value[self.best_move_captures_piece_type] > piece_to_value[self.best_move_piece_type]
    #     else:
    #         return False
    #
    # def is_hanging(self):

    # def pieces_attacked(self):
    #     board = self.board.copy()
    #     board.push(self.move)
    #     attacks_mask = board.attacks_mask(self.move.to_square)
    #     pieces_attacked_mask = attacks_mask & self.board.occupied_co[self.board.turn]
    #     self.board.pop()
    #     return chess.popcount(pieces_attacked_mask)

    # def best_move_piece_types_attacked(self):
    #     board = self.board.copy()
    #     board.push(self.move)
    #     attacks_mask = board.attacks(self.move.to_square)
    #     their_pieces_mask = board.occupied_co[self.board.turn]
    #     pieces_attacked_mask = attacks_mask & their_pieces_mask
    #
    #
    #     return chess.popcount(pieces_attacked_mask)


    # def higher_value_pieces_attacked(self):

    # def defends_hanging_piece(self):
        # our hanging piece count before and after move?

    # TODO: threatens fork.

    # TODO: two different pieces are attacking two different majors? Discovered attack on queen.
    # def minors_attacking_majors_after_best_move(self):
    #     board = self.board.copy()
    #
    #     our_color = board.turn
    #     their_color = not board.turn
    #     their_queen_mask = board.pieces_mask(chess.QUEEN, their_color)
    #     their_rook_mask = board.pieces_mask(chess.ROOK, their_color)
    #     their_major_mask = their_queen_mask | their_rook_mask
    #
    #     board.push(self.move)
    #
    #     def square_is_attacked_by_minor(color, square):
    #         for attacker in board.attackers(color, square):
    #             attacker_piece_type = board.piece_type_at(attacker)
    #             if attacker_piece_type in [chess.KNIGHT, chess.BISHOP]:
    #                 return True
    #         return False
    #
    #     count = 0
    #     for major in chess.scan_forward(their_major_mask):
    #         count += square_is_attacked_by_minor(our_color, major)
    #     return count
    #
    #
    # def higher_value_pieces_attacked_after_best_move(self):
    #     board = self.board.copy()
    #     our_color = board.turn
    #     their_color = not board.turn
    #     their_pieces = board.occupied_co[their_color]
    #     their_non_pawns = their_pieces & ~board.pawns
    #
    #     board.push(self.move)
    #
    #     def square_is_attacked_by_lower_value(color, square):
    #         attacked_piece_type = board.piece_type_at(square)
    #         for attacker in board.attackers(color, square):
    #             attacker_piece_type = board.piece_type_at(attacker)
    #             if (attacker_piece_type == chess.KNIGHT and attacked_piece_type == chess.BISHOP):
    #                 continue
    #             if attacker_piece_type < attacked_piece_type:
    #                 return True
    #         return False
    #
    #     count = 0
    #     for square in chess.scan_forward(their_non_pawns):
    #         count += square_is_attacked_by_lower_value(our_color, square)
    #     return count


class BestPV(Features):

    def __init__(self, fen, pv):
        self.board = chess.Board(fen)
        self.pv = [chess.Move.from_uci(move) for move in eval(pv)]

    @classmethod
    def from_row(cls, row):
        return cls(row.fen, row.best_pv)

    @staticmethod
    def _number_of_captures(board, pv, color):
        count = 0
        board = board.copy() # TODO: do we need to copy here?
        for move in pv:
            count += (board.turn == color and board.is_capture(move))
            board.push(move)
        return count

    @staticmethod
    def _number_of_checks(board, pv, color):
        count = 0
        board = board.copy()
        for move in pv:
            board.push(move)
            count += (board.turn == color and board.is_check())
        return count

    @staticmethod
    def _number_of_pieces_moved(board, pv, color):
        board = board.copy()
        squares = set()
        count = 0
        for move in pv:
            if board.turn == color:
                if move.from_square in squares:
                    squares.remove(move.from_square)
                else:
                    count += 1
            board.push(move)
            squares.add(move.to_square)
        return count

    @cached_property
    def best_pv_our_number_of_captures(self):
        return self._number_of_captures(self.board, self.pv, self.board.turn)

    @cached_property
    def best_pv_their_number_of_captures(self):
        return self._number_of_captures(self.board, self.pv, not self.board.turn)

    @cached_property
    def best_pv_our_number_of_checks(self):
        return self._number_of_checks(self.board, self.pv, self.board.turn)

    @cached_property
    def best_pv_their_number_of_checks(self):
        return self._number_of_checks(self.board, self.pv, not self.board.turn)

    @cached_property
    def best_pv_our_number_of_pieces_moved(self):
        return self._number_of_pieces_moved(self.board, self.pv, self.board.turn)

    @cached_property
    def best_pv_their_number_of_pieces_moved(self):
        return self._number_of_pieces_moved(self.board, self.pv, not self.board.turn)


class TheirKing(Features):

    def __init__(self, fen):
        self.board = chess.Board(fen)

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
    def their_piece_count_in_king_ring(self):
        their_color = not self.board.turn
        their_king = self.board.king(their_color)
        their_king_ring_mask = self.board.attacks_mask(their_king)
        their_pieces_mask = self.board.occupied_co[their_color]
        return chess.popcount(their_king_ring_mask & their_pieces_mask)

    # @cached_property
    # def our_piece_count_in_king_ring(self):
    #     their_king_ring_mask = self._their_king_ring_mask
    #     our_pieces_mask = self.board.occupied_co[our_color]
    #     return chess.popcount(their_king_ring_mask & our_pieces_mask)

    # TODO: our defended pieces in king ring.

    @cached_property
    def _their_king_ring_mask(self):
        their_color = not self.board.turn
        their_king = self.board.king(their_color)
        return self.board.attacks_mask(their_king)

    @cached_property
    def _our_attacks_mask(self):
        our_attacks_mask = chess.BB_EMPTY
        our_pieces_mask = self.board.occupied_co[self.board.turn]
        for square in chess.scan_reversed(our_pieces_mask):
            our_attacks_mask |= self.board.attacks_mask(square)
        return our_attacks_mask

    @cached_property
    def _their_attacks_mask(self):
        their_king = self.board.king(not self.board.turn)
        their_attacks_mask = chess.BB_EMPTY
        their_pieces_mask = self.board.occupied_co[not self.board.turn]
        for square in chess.scan_reversed(their_pieces_mask):
            if square != their_king:
                their_attacks_mask |= self.board.attacks_mask(square)
        return their_attacks_mask


    @cached_property
    def their_empty_king_ring_squares_attacked(self):
        their_color = not self.board.turn
        their_pieces_mask = self.board.occupied_co[their_color]
        return chess.popcount(
            self._their_king_ring_mask &
            self._our_attacks_mask &
            ~their_pieces_mask
        )

    @cached_property
    def their_empty_king_ring_squares_defended(self):
        their_color = not self.board.turn
        their_pieces_mask = self.board.occupied_co[their_color]
        return chess.popcount(
            self._their_king_ring_mask &
            self._their_attacks_mask &
            ~their_pieces_mask
        )

    @cached_property
    def their_pawns_in_their_king_ring_count(self):
        their_color = not self.board.turn
        their_pawns_mask = self.board.pieces_mask(chess.PAWN, their_color)
        return chess.popcount(their_pawns_mask & self._their_king_ring_mask)




    # @cached_property
    # def our_pieces_attacking_their_king_ring(self:)



    # @cached_property
    # def best_move_is_captured(self):
    #     if len(self.pv) == 1: return False
    #     return self.pv[0].to_square == self.pv[1].to_square
    #
    # # TODO: redundent with best move?
    # @cached_property
    # def pv0_is_capture(self):
    #     return self.board.is_capture(self.pv[0])
    #
    # @cached_property
    # def pv2_is_capture(self):
    #     if len(self.pv) < 3: return 0
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     board.push(self.pv[1])
    #     return board.is_capture(self.pv[2])
    #
    # @cached_property
    # def pv0_piece_type(self):
    #     return self.board.piece_type_at(self.pv[0].from_square)

    # def pv1_piece_type(self):
    #     if len(self.pv) < 2: return 0
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     return self.board.piece_type_at(self.pv[1].from_square)
    #
    # @cached_property
    # def pv2_piece_type(self):
    #     if len(self.pv) < 3: return 0
    #
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     board.push(self.pv[1])
    #     return self.board.piece_type_at(self.pv[2].from_square)

    # TODO: separate this into attacked by moved piece and attacked in general.
    # def pv0_piece_types_attacked(self):
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     attacks_mask = board.attacks_mask(self.pv[0].to_square)
    #     their_pieces_mask = board.occupied_co[board.turn]
    #     pieces_attacked_mask = attacks_mask & their_pieces_mask
    #     piece_types_attacked = []
    #     for square in chess.scan_forward(pieces_attacked_mask):
    #         piece_types_attacked.append(board.piece_type_at(square))
    #     return piece_types_attacked

    # TODO: make this a by piece function
    # TODO: how to combine all these?
    # TODO: compute this from cached pv0_piece_types_attacked?
    # @cached_property
    # def pv0_higher_value_pieces_attacked(self):
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     piece_type = board.piece_type_at(self.pv[0].to_square)
    #     attacks_mask = board.attacks_mask(self.pv[0].to_square)
    #     their_pieces_mask = board.occupied_co[board.turn]
    #     pieces_attacked_mask = attacks_mask & their_pieces_mask
    #     higher_value_pieces_attacked = 0
    #     for square in chess.scan_forward(pieces_attacked_mask):
    #         piece_type_attacked = board.piece_type_at(square)
    #         higher_value_pieces_attacked += is_higher_value(piece_type_attacked, piece_type)
    #     return higher_value_pieces_attacked
    #
    # @cached_property
    # def pv0_is_attacked(self):
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     return board.is_attacked_by(board.turn, self.pv[0].to_square)
    #
    # @cached_property
    # def pv2_is_attacked(self):
    #     if len(self.pv) < 3: return 0
    #     board = self.board.copy()
    #     their_color = not board.turn
    #     board.push(self.pv[0])
    #     board.push(self.pv[1])
    #     board.push(self.pv[2])
    #     return board.is_attacked_by(their_color, self.pv[2].to_square)
    #
    # @cached_property
    # def pv0_is_knight_fork(self):
    #     return (
    #         self.pv0_piece_type == 2 and
    #         self.pv0_higher_value_pieces_attacked >= 2 and
    #         self.pv0_is_attacked == False
    #
    #     )
    #
    # @cached_property
    # def attacks_on_higher_value_pieces(self):
    #     return attacks_on_higher_value_pieces(self.board, self.board.turn)
    #
    # TODO: convert this to a function that takes a board and color.
    # @cached_property
    # def pv0_attacks_on_higher_value_pieces(self):
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     return attacks_on_higher_value_pieces(board, not board.turn)
    #
    # @cached_property
    # def pv0_capture_piece_type(self):
    #     if self.board.is_capture(self.pv[0]):
    #         return self.board.piece_type_at(self.pv[0].to_square)
    #     else:
    #         return 0
    #
    # @cached_property
    # def pv0_is_capture_higher_value(self):
    #     return is_higher_value(self.pv0_capture_piece_type, self.pv0_piece_type)
    #
    # @cached_property
    # def pv0_is_capture_hanging_piece(self):
    #     return (
    #         self.pv0_is_capture and
    #         not self.pv0_is_attacked
    #     )
    #
    #
    # @cached_property
    # def pv2_captures_higher_value(self):
    #     return is_higher_value(self.pv2_capture_piece_type, self.pv2_piece_type)
    #
    # @cached_property
    # def pv2_captures_hanging_piece(self):
    #     return self.pv2_is_capture and not self.pv2_is_attacked

    # def pv1_capture_piece_type(self):
    #     if len(self.pv) < 2: return 0
    #
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     if board.is_capture(self.pv[1]):
    #         return board.piece_type_at(self.pv[1].to_square)
    #     else:
    #         return 0
    #
    # @cached_property
    # def pv2_capture_piece_type(self):
    #     if len(self.pv) < 3: return 0
    #
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     board.push(self.pv[1])
    #     if board.is_capture(self.pv[2]):
    #         return board.piece_type_at(self.pv[2].to_square)
    #     else:
    #         return 0
    #
    # def pv0_is_check(self):
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     return board.is_check()
    #
    # def pv1_is_check(self):
    #     if len(self.pv) < 2: return False
    #
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     board.push(self.pv[1])
    #     return board.is_check()
    #
    # def pv2_is_check(self):
    #     if len(self.pv) < 3: return False
    #
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     board.push(self.pv[1])
    #     board.push(self.pv[2])
    #     return board.is_check()
    #
    # def pv0_is_discovered_check(self):
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #
    #     attacks_mask = board.attacks_mask(self.pv[0].to_square)
    #     their_king_mask = board.pieces_mask(chess.KING, board.turn)
    #     return board.is_check() and not (attacks_mask & their_king_mask)
    #
    # def moves_same_piece_twice(self):
    #     return (
    #         len(self.pv) > 2 and
    #         self.pv[0].to_square == self.pv[2].from_square
    #     )
    #
    # # TODO: handle trap that doesn't attack current queen square.
    # def pv0_traps_queen(self):
    #     board = self.board.copy()
    #     our_color = board.turn
    #     their_color = not board.turn
    #     their_queens_mask = board.pieces_mask(chess.QUEEN, their_color)
    #
    #     # TODO: handle multiple queens later
    #     if chess.popcount(their_queens_mask) > 1: return False
    #
    #     # TODO: attacks queen and all her moves.
    #     board.push(self.pv[0])
    #
    #     if board.is_check(): return False
    #
    #     best_move_attacks_mask = board.attacks_mask(self.pv[0].to_square)
    #
    #     if (best_move_attacks_mask & their_queens_mask):
    #         queen = list(chess.scan_forward(their_queens_mask)).pop()
    #
    #         min_attackers = []
    #         queen_moves = [move for move in board.legal_moves if move.from_square == queen]
    #
    #         def square_is_attacked_by_lower_value(square):
    #             for attacker in board.attackers(our_color, square):
    #                 attacker_piece_type = board.piece_type_at(attacker)
    #                 if attacker_piece_type not in [5, 6]:
    #                     return True
    #
    #         queen_moves_are_attacked = [square_is_attacked_by_lower_value(move.to_square) for move in queen_moves]
    #
    #         return all(queen_moves_are_attacked)

    # @cached_property
    # def hanging_pieces(self):
    #     return hanging_pieces(self.board, self.board.turn)
    #
    # @cached_property
    # def pv0_hanging_pieces(self):
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     return hanging_pieces(board, not board.turn)


def is_higher_value(a, b):
    piece_type_to_value = {
        None: 0,
        0: 0,
        1: 1,
        2: 3,
        3: 3,
        4: 5,
        5: 8,
        6: 10,
    }
    return piece_type_to_value[a] > piece_type_to_value[b]


def is_attacked_by_lower_value(board, color, square):
    piece_type = board.piece_type_at(square)
    for attacker in board.attackers(color, square):
        attacker_piece_type = board.piece_type_at(attacker)
        if is_higher_value(piece_type, attacker_piece_type):
            return True
    return False


def attacks_on_higher_value_pieces(board, color):
    pieces_mask = board.occupied_co[not color]

    attacks_on_higher_value_pieces = 0
    for square in chess.scan_forward(pieces_mask):
        attacks_on_higher_value_pieces += is_attacked_by_lower_value(board, color, square)

    return attacks_on_higher_value_pieces


def hanging_pieces(board, color):
    pieces = board.occupied_co[color]
    hanging_pieces = 0
    for piece in chess.scan_forward(pieces):
        is_attacked = board.is_attacked_by(not color, piece)
        is_defended = board.is_attacked_by(color, piece)
        hanging_pieces += is_attacked and not is_defended
    return hanging_pieces


class ThreatFeatures():

    def __init__(self, fen):
        self.board = chess.Board(fen)

    def minors_attacking_majors(self):
        their_color = not self.board.turn
        their_queen_mask = self.board.pieces_mask(chess.QUEEN, their_color)
        their_rook_mask = self.board.pieces_mask(chess.ROOK, their_color)
        their_major_mask = their_queen_mask | their_rook_mask

        def square_is_attacked_by_minor(color, square):
            for attacker in self.board.attackers(color, square):
                attacker_piece_type = self.board.piece_type_at(attacker)
                if attacker_piece_type in [chess.KNIGHT, chess.BISHOP]:
                    return True
            return False

        count = 0
        for major in chess.scan_forward(their_major_mask):
            count += square_is_attacked_by_minor(self.board.turn, major)
        return count

    def higher_value_pieces_attacked(self):
        board = self.board.copy()
        our_color = board.turn
        their_color = not board.turn
        their_pieces = board.occupied_co[their_color]
        their_non_pawns = their_pieces & ~board.pawns

        def square_is_attacked_by_lower_value(color, square):
            attacked_piece_type = board.piece_type_at(square)
            for attacker in board.attackers(color, square):
                attacker_piece_type = board.piece_type_at(attacker)
                if (attacker_piece_type == chess.KNIGHT and  attacked_piece_type == chess.BISHOP):
                    continue
                if attacker_piece_type < attacked_piece_type:
                    return True
            return False

        count = 0
        for square in chess.scan_forward(their_non_pawns):
            count += square_is_attacked_by_lower_value(our_color, square)
        return count


def stockfish_info(engine, fen, move=None, depth=10, multipv=None):
    board = chess.Board(fen)
    move = [chess.Move.from_uci(move)] if move else None
    return engine.analyse(
        board,
        root_moves=move,
        multipv=multipv,
        limit=chess.engine.Limit(depth=depth)
    )


class StockfishFeatures():

    def __init__(self, fen, engine):
        info = stockfish_info(engine, fen, depth=2, multipv=500)
        self.pvs = [pv['pv'] for pv in info]
        self.scores = [pv['score'] for pv in info]

    @cached_property
    def their_mates(self):
        mates = 0
        for score in self.scores:
            if score.is_mate():
                mates += score.relative.mate() < 0
        return mates

    @cached_property
    def pv_variation(self):
        moves = []
        for pv in self.pvs:
            if len(pv) > 1:
                moves.append(pv[1])
        return len(set(moves)) / len(moves)


# TODO: how to put this into class? From row...
def get_features(row, cls, engine=None):
    if cls == MateIn1Features:
        instance = cls(row.fen, row.best_pv)
    elif cls == StockfishFeatures:
        instance = cls(row.fen, engine)
    elif cls == MoveFeatures:
        instance = cls(row.fen, row.best_move)
    elif cls == Features:
        instance = cls(row.fen, row.best_pv)
    else:
        instance = cls(row.fen)
    features = {}
    for feature_name in class_features(cls):
        features[feature_name] = getattr(instance, feature_name)
    return features


def get_df(df, feature_classes, include_columns=[]):
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    feature_dfs = []
    for cls in feature_classes:
        if cls == StockfishFeatures:
            feature_df = df.progress_apply(get_features, cls=cls, engine=engine, result_type='expand', axis=1)
        else:
            feature_df = df.progress_apply(get_features, cls=cls, result_type='expand', axis=1)
        feature_dfs.append(feature_df)
    feature_df = pd.concat(feature_dfs, axis=1)

    for column in include_columns:
        feature_df[column] = df[column]

    engine.quit()

    return feature_df
