from functools import cached_property

import chess

from board import AugBoard
from board.motives.fork import is_fork_see as is_fork
from board.motives.skewer import is_skewer_see as is_skewer
from board.motives.pin import is_pin_see as is_pin
from board.motives.discovered_attack import (
    is_discovered_attack_see as is_discovered_attack,
)
from board.motives.sacrifice import is_sacrifice_see as is_sacrifice
from features.abstract import Features


class Motives(Features):

    csvs = ["lichess", "stockfish10"]

    def __init__(self, fen, pv):
        self.fen = fen
        self.pv = [chess.Move.from_uci(move) for move in eval(pv)]

    @classmethod
    def from_row(cls, row):
        return cls(row.fen, row.best_pv)

    @staticmethod
    def _contains_motive(fen, pv, motive_finder):
        aug = AugBoard(fen)
        for i in range(0, len(pv), 2):
            our_move = pv[i]
            if motive_finder(aug.fen(), our_move):
                return True
            aug.push(our_move)
            if i + 1 < len(pv):
                their_move = pv[i + 1]
                aug.push(their_move)
        return False

    @cached_property
    def is_first_move_fork(self):
        return self._contains_motive(self.fen, self.pv[:1], is_fork)

    @cached_property
    def is_first_move_discovered_attack(self):
        return self._contains_motive(self.fen, self.pv[:1], is_discovered_attack)

    @cached_property
    def is_first_move_skewer(self):
        return self._contains_motive(self.fen, self.pv[:1], is_skewer)

    @cached_property
    def is_first_move_pin(self):
        return self._contains_motive(self.fen, self.pv[:1], is_pin)

    @cached_property
    def is_first_move_sacrifice(self):
        return self._contains_motive(self.fen, self.pv[:1], is_sacrifice)
