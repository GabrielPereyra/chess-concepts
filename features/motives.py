from functools import cached_property

import chess

from features.abstract import Features
from features.helpers import get_attacking
from features.helpers import (
    is_lower_value,
    is_lower_equal_value,
    is_greater_value,
    is_greater_equal_value,
    is_same_value,
)


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
    Let S be the set of pairs of squares (a, b) such that our piece at square a attacks their piece at square b
    such that their piece at square b is either undefended or has a higher values
    Let S1 be S before our move
    Let S2 be S after our move and excluding pieces attacked by the piece that was moved
    We define that the move is discovered attack iff. there exists an element in S2 that is not in S1
    """

    board = chess.Board(fen)
    our_color = board.turn

    attackers_before_move = get_attacking(
        board, our_color, piece_type_filter=is_lower_value
    )
    attackers_before_move.update(
        get_attacking(board, our_color, attacked_is_defended=False)
    )
    board.push(move)

    attackers_after_move = get_attacking(
        board, our_color, piece_type_filter=is_lower_value
    )
    attackers_after_move.update(
        get_attacking(board, our_color, attacked_is_defended=False)
    )

    attackers_after_move = {
        (attacking, attacked)
        for attacking, attacked in attackers_after_move
        if attacking != move.to_square
    }

    return bool(attackers_after_move - attackers_before_move)


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
        if (not attacker_is_attacked or attacker_is_defended) and (
            not attacked_has_lower_equal_value or not attacked_attacks_attacker
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

    Their piece is attacked by our piece of a lower value that is either defended or not attacked.

    When their attacked piece is removed from the board, our attacking piece attack their another,
    previously not attacked, piece of at least the same value.

    NOTE: it will classify some of the examples as skewers that probably shouldn't be called skewers.
    Example is a position where we attack their queen with our rook. If the queen moves, then it discovers our attack
    on their rook, but actually the queen can move in such a way that it will defend their rook.
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
        attacker_is_attacked = bool(board.attackers(their_color, attacker))
        attacker_is_defended = bool(board.attackers(our_color, attacker))
        if not attacker_is_attacked or attacker_is_defended:
            board_without_attacked = board.copy()
            board_without_attacked.remove_piece_at(attacked)
            new_attackers = get_attacking(
                board_without_attacked, our_color, is_lower_equal_value
            )
            if new_attackers - attackers_after_move:
                return True
    return False


class Motives(Features):
    def __init__(self, fen, pv):
        self.board = chess.Board(fen)
        self.pv = [chess.Move.from_uci(move) for move in eval(pv)]
        self.our_color = self.board.turn
        self.their_color = not self.board.turn

    @classmethod
    def from_row(cls, row):
        return cls(row.fen, row.best_pv)

    @cached_property
    def contains_fork(self):
        return contains_fork(self.board.fen(), self.pv)

    @cached_property
    def is_first_move_fork(self):
        return contains_fork(self.board.fen(), self.pv[:3])

    @cached_property
    def contains_discovered_attack(self):
        board = self.board.copy()
        for i in range(0, len(self.pv), 2):
            our_move = self.pv[i]
            if is_discovered_attack(board.fen(), our_move):
                return True
            board.push(our_move)
            if i + 1 < len(self.pv):
                their_move = self.pv[i + 1]
                board.push(their_move)
        return False

    @cached_property
    def is_first_move_discovered_attack(self):
        return is_discovered_attack(self.board.fen(), self.pv[0])

    @cached_property
    def contains_skewer(self):
        board = self.board.copy()
        for i in range(0, len(self.pv), 2):
            our_move = self.pv[i]
            if is_skewer(board.fen(), our_move):
                return True
            board.push(our_move)
            if i + 1 < len(self.pv):
                their_move = self.pv[i + 1]
                board.push(their_move)
        return False

    @cached_property
    def is_first_move_skewer(self):
        return is_skewer(self.board.fen(), self.pv[0])

    @cached_property
    def contains_pin(self):
        board = self.board.copy()
        for i in range(0, len(self.pv), 2):
            our_move = self.pv[i]
            if is_pin(board.fen(), our_move):
                return True
            board.push(our_move)
            if i + 1 < len(self.pv):
                their_move = self.pv[i + 1]
                board.push(their_move)
        return False

    @cached_property
    def is_first_move_pin(self):
        return is_pin(self.board.fen(), self.pv[0])


if __name__ == "__main__":
    fen = "1kq5/1pp5/p3b3/8/8/8/5NQP/5BK1 w - - 0 1"
    move = chess.Move.from_uci("g2h3")
    res = is_pin(fen, move)
    print(res)
