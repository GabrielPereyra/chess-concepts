from functools import cached_property

import numpy as np

from features import StockfishDepth
from features.abstract import Features

"""
These are classes that convert original features to primite types that 
can be used in a machine learning model
"""


class StockfishDepthStats(Features):
    def __init__(self, fen, p, best_move):
        self.stockfish_depth = StockfishDepth(fen, p)
        self.stockfish_features = self.stockfish_depth.features()
        self.best_move = best_move

    @cached_property
    def score_variance(self):
        try:
            return np.var(self.stockfish_features["scores"])
        except:
            return -1

    @cached_property
    def mate_variance(self):
        try:
            return np.var(self.stockfish_features["mates"])
        except:
            return -1

    @cached_property
    def best_move_index(self):
        return (
            self.stockfish_features["moves"].index(self.best_move)
            if self.best_move in self.stockfish_features["moves"]
            else -1
        )
