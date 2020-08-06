from functools import cached_property

import chess

STOCKFISH_PATH = '../Stockfish/src/stockfish'


def stockfish_info(engine, fen, move=None, depth=10, multipv=None):
    board = chess.Board(fen)
    move = [chess.Move.from_uci(move)] if move else None
    return engine.analyse(
        board,
        root_moves=move,
        multipv=multipv,
        limit=chess.engine.Limit(depth=depth)
    )


# TODO: shouldn't it derive from Features base class?
class StockfishFeatures():

    def __init__(self, fen, engine):
        info = stockfish_info(engine, fen, depth=2, multipv=500)
        self.pvs = [pv['pv'] for pv in info]
        self.scores = [pv['score'] for pv in info]

    @cached_property
    def their_mates(self):
        mates = 0
        for score in self.scores:
            if score.is_mate():
                mates += score.relative.mate() < 0
        return mates

    @cached_property
    def pv_variation(self):
        moves = []
        for pv in self.pvs:
            if len(pv) > 1:
                moves.append(pv[1])
        return len(set(moves)) / len(moves)


