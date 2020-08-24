from ast import literal_eval
from functools import cached_property

import chess

from board import AugBoard
from board.mates import is_back_rank_mate, is_smothered_mate, is_arabian_mate_extended

from features.abstract import Features


class CheckmateType(Features):
    def __init__(self, fen, pv):
        aug = AugBoard(fen)
        pv = [chess.Move.from_uci(move) for move in literal_eval(pv)]
        for move in pv[:-1]:
            aug.push(move)
        self.fen = aug.fen()
        self.move = pv[-1]

        if not aug.gives_checkmate(self.move):
            print("wtf")

    @classmethod
    def from_row(cls, row):
        return cls(row.fen, row.best_pv)

    @cached_property
    def is_back_rank_mate(self):
        return is_back_rank_mate(self.fen, self.move)

    @cached_property
    def is_smothered_mate(self):
        return is_smothered_mate(self.fen, self.move)

    @cached_property
    def is_arabian_mate(self):
        return is_arabian_mate_extended(self.fen, self.move)
