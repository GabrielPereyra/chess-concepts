from features.move import Move


class UserMove(Move):

    # TODO: replace this with an attribute which specifies columns
    @classmethod
    def from_row(cls, row):
        return cls(row.fen, row.move)

    def features(self, prefix=None):
        return super(UserMove, self).features(prefix="user_move")
