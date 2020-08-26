from ast import literal_eval
from typing import Iterable
from functools import cached_property

import chess

from board import AugBoard

from features.abstract import Features


class CheckmateType(Features):

    csvs = ["lichess", "stockfish10"]

    def __init__(self, fen: str, pv: Iterable[str]):
        self.aug = AugBoard(fen)
        pv = [chess.Move.from_uci(move) for move in pv]
        for move in pv[:-1]:
            self.aug.push(move)
        self.move = pv[-1]

    @classmethod
    def from_row(cls, row):
        return cls(row.fen, literal_eval(row.best_pv))

    def _checkmate_types(self):
        return self.aug.move_checkmate_types(self.move)

    # TODO: consider changing return type so it can handle multiple tactics
    @cached_property
    def checkmate_type(self):
        return self._checkmate_types()[0]
