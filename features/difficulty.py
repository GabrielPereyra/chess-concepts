from functools import cached_property

import chess

from features.abstract import Features
from sklearn.linear_model import LogisticRegression


class Difficulty(Features):
    """Difficulty of a position is probability of blunder estimate by model."""

    # TODO: how to define the features we use.
    # csvs = ["lichess", "stockfish10"]

    @classmethod
    def from_df(cls, df):

        import pdb

        pdb.set_trace()

        # TODO: extract X and y, train sklearn model, return feature_df
