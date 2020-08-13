from functools import cached_property

import chess

from features.abstract import Features


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
