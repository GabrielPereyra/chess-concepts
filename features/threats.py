import chess
import itertools
import pandas as pd
pd.set_option('display.max_rows', 1000)


PIECE_TYPE_VALUE = {
    None: 0,
    1: 1,
    2: 3,
    3: 3,
    4: 5,
    5: 9,
    6: 10,
}


class Square():

    def __init__(self, board, square):
        self.square = square
        self.rank = chess.square_rank(square)
        self.file = chess.square_file(square)
        self.is_light = bool(square % 2)


class Piece():

    # TODO: is_minor / major / slider?

    def __init__(self, board, square):
        self.square = square
        self.piece_type = board.piece_type_at(square)
        self.color = board.color_at(square)
        self.value = PIECE_TYPE_VALUE[self.piece_type]
        # self.is_pinned = board.is_pinned(self.color, square)

    @classmethod
    def df(cls, board):
        pieces = chess.scan_reversed(board.occupied)
        df = pd.DataFrame([cls(board, p).__dict__ for p in pieces])
        return df.set_index('square')


class Move():

    def __init__(self, board, move):
        self.from_square = move.from_square
        self.to_square = move.to_square
        self.piece_type = board.piece_type_at(self.from_square)
        self.gives_check = board.gives_check(move)
        self.is_capture = board.is_capture(move)
        # self.is_en_passant = board.is_en_passant(move)
        # self.is_castling = board.is_castling(move)

    @classmethod
    def df(cls, board):
        return pd.DataFrame([cls(board, m).__dict__ for m in board.legal_moves])


class Moves():

    def __init__(self, fen):
        df = Move.df(chess.Board(fen))
        self.num_moves = len(df)
        self.reachable_squares = len(df['to_square'].unique())
        self.num_checks = df['gives_check'].sum()
        self.num_captures = df['is_capture'].sum()


class Pieces():

    def __init__(self, fen):
        df = Piece.df(chess.Board(fen))

        piece_counts = df.groupby(['color', 'piece_type']).size()
        for (color, piece_type), count in piece_counts.iteritems():
            piece_name = chess.PIECE_NAMES[piece_type]
            whose = 'our' if color == board.turn else 'their'
            setattr(self, '{}_{}_count'.format(whose, piece_name), count)


class Attack():

    def __init__(self, attacking, attacked):
        self.attacking = attacking
        self.attacked = attacked

    @classmethod
    def df(cls, board):
        attacks = []
        for attacking in chess.scan_reversed(board.occupied):
            for attacked in board.attacks(attacking):
                attacks.append(Attack(attacking, attacked).__dict__)
        return pd.DataFrame(attacks)


# our attacked / their attacked
class AttackedPieces():

    def __init__(self, fen):
        board = chess.Board(fen)
        piece_df = Piece.df(board)
        attack_df = Attack.df(board)

        df = attack_df.merge(piece_df, left_on='attacking', right_index=True)
        df = df.merge(piece_df, left_on='attacked', right_index=True, suffixes=('_attacking', '_attacked'))

        df['is_attacked_by_lower_value'] = df['value_attacked'] > df['value_attacking']

        df.groupby(['color_attacking', 'color_attacked',  'attacked']).agg({'is_attacked_by_lower_value': any})

        import pdb; pdb.set_trace()



if __name__ == '__main__':
    df = pd.read_csv('csvs/lichess/0-00/0.csv')
    fen = df['fen'][38]
    print(chess.Board(fen))
    AttackedPieces(fen)
