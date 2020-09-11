from features.move import Move


class BestMove(Move):

    # TODO: replace this with an attribute which specifies columns
    @classmethod
    def from_row(cls, row):
        return cls(row.fen, row.best_move)

    def features(self, prefix=None):
        return super(BestMove, self).features(prefix="best_move")
