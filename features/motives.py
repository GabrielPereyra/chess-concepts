from functools import cached_property

import chess

from features.abstract import Features
from features.helpers import get_attacking
from features.helpers import (
    is_lower_value,
    is_lower_equal_value,
    is_greater_value,
)
from features.helpers import count_material, PIECE_TYPE_VALUE


def contains_fork(fen, pv):
    """
    We consider a move a fork when it attacks two or more opponent's pieces and next some of these pieces is captured
    by the piece that forked it.
    Conditions
    - at some point in the pv, our piece must be moved so that it attacks two or more opponent's pieces
    - then opponent makes their move
    - and finally we capture one of the forked pieces
    """

    if len(pv) < 3:
        return False

    board = chess.Board(fen)
    their_color = not board.turn

    for i in range(0, len(pv) - 2, 2):
        first, response, second = pv[i : i + 3]
        board.push(first)
        mask = board.occupied_co[their_color] & board.attacks_mask(first.to_square)
        board.push(response)
        if chess.popcount(mask) >= 2:
            if mask & chess.BB_SQUARES[second.to_square]:
                return True
    return False


def is_discovered_attack(fen: str, move: chess.Move) -> bool:
    """
    A discovered attack can be only performed by a queen, rook or bishop.

    We define a discovered attack as a move from square in a ray of two other squares, let's call them X and Y, such
    that our piece A is on square X, their piece B is on square Y and:
    - A attacks B
    - B has greater value than A or B is not defended
    - None of their pieces attack A or A is defended or the moved piece checks their king
    """

    board = chess.Board(fen)
    our_color = board.turn
    their_color = not our_color

    board.push(move)

    attackers_after_move = get_attacking(
        board, our_color, piece_type_filter=is_lower_value
    )
    attackers_after_move.update(
        get_attacking(board, our_color, attacked_is_defended=False)
    )

    return bool(
        [
            (attacker, attacked)
            for attacker, attacked in attackers_after_move
            if attacker != move.to_square
            and move.from_square in chess.SquareSet.ray(attacker, attacked)
            and (
                board.is_attacked_by(our_color, attacker)
                or not board.is_attacked_by(their_color, attacker)
                or move.to_square in board.checkers()
            )
        ]
    )


def is_pin(fen: str, move: chess.Move) -> bool:
    """
    Can be only performed by a queen, rook or bishop

    Their piece (called pinned) is attacked by our piece (called pinning) that is either defended or not attacked.
    Moreover, if the pinned piece is of value not greater than the pinning piece, the pinned piece must not be attacking
    the pinning piece even if the pinning piece is defended.

    When the pinned piece is removed from the board, the pinning piece attacks their another, previously not attacked,
    piece of a greater value than the pinned piece.

    NOTE #1: it will classify some of the examples as pins that probably shouldn't be called pins.

    - One of such examples is a "relative pin" where the pinned piece can move and avoid the attacker to capture
    the more valuable piece. For instance, if we pin a rook to a queen but the rook can be moved with check forcing us
    to react instead of capturing the queen. It's up for discussion if it's a pin or not:
    https://lichess.org/analysis/1kq5/1pp5/p3r3/8/8/8/5PBP/3Q2K1_w_-_-_0_1

    - Another example is quite tricky one, called situational pin: https://en.wikipedia.org/wiki/Pin_(chess)#Situational_pin
    For instance, when a piece is pinned to a critical square instead to another piece

    NOTE #2: in future, it might be worth to consider a more detailed classification into relative and absolute pins.
    One way to do it is to change the return type of is_pin to return also pinning and pinned piece types and use them
    for a more detailed classification.
    """

    board = chess.Board(fen)

    if board.piece_type_at(move.from_square) not in [
        chess.QUEEN,
        chess.ROOK,
        chess.BISHOP,
    ]:
        return False

    our_color = board.turn
    their_color = not board.turn
    attackers_before_move = get_attacking(board, our_color)
    board.push(move)

    attackers_after_move = get_attacking(board, our_color)

    for attacker, attacked in attackers_after_move - attackers_before_move:
        attacker_is_attacked = bool(board.attackers(their_color, attacker))
        attacker_is_defended = bool(board.attackers(our_color, attacker))
        attacked_attacks_attacker = attacked in board.attackers(their_color, attacker)
        attacked_has_lower_equal_value = is_lower_equal_value(
            board.piece_type_at(attacked), board.piece_type_at(attacker)
        )
        if (not attacker_is_attacked or attacker_is_defended) and not (
            attacked_attacks_attacker and attacked_has_lower_equal_value
        ):
            board_without_attacked = board.copy()
            board_without_attacked.remove_piece_at(attacked)
            new_attackers = get_attacking(board_without_attacked, our_color)
            for new_attacker, new_attacked in new_attackers - attackers_after_move:
                if new_attacker == attacker and is_greater_value(
                    board.piece_type_at(new_attacked), board.piece_type_at(attacked)
                ):
                    return True
    return False


def is_skewer(fen: str, move: chess.Move) -> bool:
    """
    Can be only performed by a queen, rook or bishop.

    Performing the move moves our piece A of value X so that it attacks their piece B of value Y such that:
    - Y > X and if A is attacked then A is defended
    - B is on a ray between A and their other piece C of value Z
    - Z <= Y
    - if B is removed from the board, then A attacks C and if C is defended then Z > X

    NOTE 1: it will classify some of the examples as skewers that probably shouldn't be called skewers.
    Example is a position where we attack their queen with our rook. If the queen moves, then it discovers our attack
    on their rook, but actually the queen can move in such a way that it will defend their rook. There is a test for this
    in the test suite but it is commented out for now.

    NOTE 2: sometimes a skewer-like attack can be blocked, it's up for discussion how do we classify these.
    """

    board = chess.Board(fen)

    if board.piece_type_at(move.from_square) not in [
        chess.QUEEN,
        chess.ROOK,
        chess.BISHOP,
    ]:
        return False

    our_color = board.turn
    their_color = not board.turn

    attackers_before_move = get_attacking(
        board, our_color, piece_type_filter=is_lower_value
    )
    board.push(move)

    attackers_after_move = get_attacking(
        board, our_color, piece_type_filter=is_lower_value
    )

    for attacker, attacked in attackers_after_move - attackers_before_move:
        attacker_attacked = bool(board.attackers(their_color, attacker))
        attacker_defended = bool(board.attackers(our_color, attacker))
        if attacker_attacked and not attacker_defended:
            continue
        attacker_piece_type = board.piece_type_at(attacker)
        board_without_attacked = board.copy()
        board_without_attacked.remove_piece_at(attacked)

        for some_attacker, new_attacked in get_attacking(
            board_without_attacked, our_color
        ):
            if some_attacker != attacker:
                continue
            new_attacked_defended = bool(
                board_without_attacked.attackers(their_color, new_attacked)
            )
            new_attacked_piece_type = board_without_attacked.piece_type_at(new_attacked)
            if new_attacked_defended and is_lower_equal_value(
                new_attacked_piece_type, attacker_piece_type
            ):
                continue

            if attacked in chess.SquareSet.ray(attacker, new_attacked):
                return True

    return False


def is_sacrifice(fen: str, move: chess.Move) -> bool:
    """
    A move is a sacrifice when the moved piece either moves to an empty square or captures a piece of a lower value
    and then there exists a series of captures at the square our first moved piece moved to, and after that series,
    our opponent gains material relatively to material balance before our first move.

    NOTE: Wikipedia proposed a division between sham and real sacrifices:
    https://en.wikipedia.org/wiki/Sacrifice_(chess)#Types_of_sacrifice
    maybe something to consider for the future.
    """

    board = chess.Board(fen)
    our_color = board.turn
    their_color = not board.turn

    material_advantage_before = count_material(board, our_color) - count_material(
        board, their_color
    )
    board.push(move)
    while True:
        next_move, lowest_value_capture = None, None

        for candidate_move in board.legal_moves:
            if candidate_move.to_square != move.to_square:
                continue
            value = PIECE_TYPE_VALUE[board.piece_type_at(candidate_move.from_square)]
            if next_move is None or value < lowest_value_capture:
                next_move = candidate_move
                lowest_value_capture = value
        if next_move is None:
            break
        board.push(next_move)

    material_advantage_after = count_material(board, our_color) - count_material(
        board, their_color
    )
    return material_advantage_after < material_advantage_before


class Motives(Features):

    csvs = ['lichess', 'stockfish10']

    def __init__(self, fen, pv):
        self.board = chess.Board(fen)
        self.pv = [chess.Move.from_uci(move) for move in eval(pv)]
        self.our_color = self.board.turn
        self.their_color = not self.board.turn

    @classmethod
    def from_row(cls, row):
        return cls(row.fen, row.best_pv)

    @staticmethod
    def _contains_simple_motive(fen, pv, motive_finder):
        board = chess.Board(fen)
        for i in range(0, len(pv), 2):
            our_move = pv[i]
            if motive_finder(board.fen(), our_move):
                return True
            board.push(our_move)
            if i + 1 < len(pv):
                their_move = pv[i + 1]
                board.push(their_move)
        return False

    # @cached_property
    # def contains_fork(self):
    #     return contains_fork(self.board.fen(), self.pv)

    @cached_property
    def is_first_move_fork(self):
        return contains_fork(self.board.fen(), self.pv[:3])

    # @cached_property
    # def contains_discovered_attack(self):
    #     return self._contains_simple_motive(
    #         self.board.fen(), self.pv, is_discovered_attack
    #     )

    @cached_property
    def is_first_move_discovered_attack(self):
        return self._contains_simple_motive(
            self.board.fen(), self.pv[:1], is_discovered_attack
        )

    # @cached_property
    # def contains_skewer(self):
    #     return self._contains_simple_motive(self.board.fen(), self.pv, is_skewer)

    @cached_property
    def is_first_move_skewer(self):
        return self._contains_simple_motive(self.board.fen(), self.pv[:1], is_skewer)

    # @cached_property
    # def contains_pin(self):
    #     return self._contains_simple_motive(self.board.fen(), self.pv, is_pin)

    @cached_property
    def is_first_move_pin(self):
        return self._contains_simple_motive(self.board.fen(), self.pv[:1], is_pin)

    # @cached_property
    # def contains_sacrifice(self):
    #     return self._contains_simple_motive(self.board.fen(), self.pv, is_sacrifice)

    @cached_property
    def is_first_move_sacrifice(self):
        return self._contains_simple_motive(self.board.fen(), self.pv[:1], is_sacrifice)
