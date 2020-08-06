from functools import cached_property

import chess

from features.abstract import Features


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