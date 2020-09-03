import os
import click
import pandas as pd
import subprocess
from functools import cached_property

from features.abstract import Features


# TODO: add link to forked version that prints features.
ETHEREAL_PATH = os.environ.get("ETHEREAL_PATH", "../Ethereal/src/Ethereal")


class EtherealEval(Features):
    def __init__(self, fen, p):
        p.stdin.write("position fen {}\n".format(fen))
        p.stdin.write("go depth 1\n")

        p.stdout.readline()  # eval
        features = eval(p.stdout.readline())
        p.stdout.readline()  # bestmove

        _features = {}
        turn = fen.split()[1]
        for feature, value in features.items():
            color, name = feature.split("_", 1)
            if color == turn:
                _features["our_{}".format(name)] = value
            else:
                _features["their_{}".format(name)] = value
        self._features = _features

    @classmethod
    def from_row(cls, row, p):
        return cls(row.fen, p)

    @classmethod
    def from_df(cls, df):
        p = subprocess.Popen(
            ETHEREAL_PATH,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )

        feature_rows = []
        with click.progressbar(tuple(df.itertuples())) as rows:
            for row in rows:
                feature_instance = cls.from_row(row, p)
                feature_rows.append(feature_instance.features())

        p.kill()
        return pd.DataFrame(feature_rows)

    def features(self):
        return self._features
