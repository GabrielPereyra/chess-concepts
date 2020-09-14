from features.move import Move


class PrevMove(Move):

    # TODO: replace this with an attribute which specifies columns
    @classmethod
    def from_row(cls, row):
        return cls(row.prev_fen, row.prev_move)

    def features(self, prefix=None):
        return super(PrevMove, self).features(prefix="prev_move")
