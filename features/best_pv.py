from functools import cached_property

import chess

from features.abstract import Features


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
    # def pv0_hanging_pieces(self):
    #     board = self.board.copy()
    #     board.push(self.pv[0])
    #     return hanging_pieces(board, not board.turn)