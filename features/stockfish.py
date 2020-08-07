from functools import cached_property

import click
import chess
import chess.engine
import pandas as pd

from features.abstract import Features

STOCKFISH_PATH = "../Stockfish/src/stockfish"


def stockfish_info(fen, move, engine, depth, multipv=None):
    board = chess.Board(fen)
    move = [chess.Move.from_uci(move)] if move else None
    return engine.analyse(
        board, root_moves=move, multipv=multipv, limit=chess.engine.Limit(depth=depth)
    )


class Stockfish(Features):

    # TODO: create a stockfish class that uses popen and catches all depth evals and best moves.
    # TODO: add a version that takes users move and analyzes it.
    def __init__(self, fen, engine, depth, multipv):
        self.info = stockfish_info(
            fen=fen, move=None, engine=engine, depth=depth, multipv=multipv,
        )

    @classmethod
    def from_row(cls, row, engine):
        return cls(row.fen, engine)

    @classmethod
    def from_df(cls, df):
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

        feature_rows = []
        with click.progressbar(tuple(df.itertuples())) as rows:
            for row in rows:
                feature_instance = cls.from_row(row, engine)
                feature_rows.append(feature_instance.features())

        engine.quit()
        return pd.DataFrame(feature_rows)

    @cached_property
    def best_score(self):
        return self.info["score"].relative.score()

    @cached_property
    def best_mate(self):
        return self.info["score"].relative.mate()

    @cached_property
    def best_move(self):
        return self.info["pv"][0].uci()

    @cached_property
    def best_pv(self):
        return str([move.uci() for move in self.info["pv"]])


class Stockfish10(Stockfish):
    def __init__(self, fen, engine):
        super().__init__(fen, engine, 10, None)


# TODO: how to store scores and pvs?
# class Stockfish5_500(Stockfish):
#     def __init__(self, fen, engine):
#         super().__init__(fen, engine, 5, 500)
