from functools import cached_property

import chess

from features.abstract import Features
from features.helpers import get_attacking_higher_value_piece
from features.helpers import get_attacking_undefended_piece


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

    attackers_before_move = get_attacking_higher_value_piece(board, our_color)
    attackers_before_move.update(get_attacking_undefended_piece(board, our_color))
    board.push(move)

    attackers_after_move = get_attacking_higher_value_piece(board, our_color)
    attackers_after_move.update(get_attacking_undefended_piece(board, our_color))

    attackers_after_move = {
        (attacking, attacked)
        for attacking, attacked in attackers_after_move
        if attacking != move.to_square
    }

    return bool(attackers_after_move - attackers_before_move)


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
