import chess
import chess.svg
import itertools
import pandas as pd
S3_PATH = 's3://chess-puzzles/single-best-mate/{year}-{month:0>2}/{shard}.csv'


def fen_to_svg(fen, move):
    board = chess.Board(fen)
    move = chess.Move.from_uci(move)
    arrows = [chess.svg.Arrow(move.from_square, move.to_square)]
    return chess.svg.board(
        board,
        arrows=arrows,
        size=180,
        coordinates=False,
        flipped=board.turn == chess.BLACK,
        style='svg {padding: 0px 10px 5px 0px;}'
    )


def list_isin(l, value):
    l = l.copy()
    for x in value:
        try:
            l.remove(x)
        except ValueError:
            return False
    return True


def filter_df(df, queries):
    for query in queries:
        df = df.query(query)
    return df


def df_to_boards(df):
    html = []
    for fen, move in zip(df['fen'], df['best_move']):
        html.append(fen_to_svg(fen, move))
    return ''.join(html)


def df_to_table(df, columns=[]):
    df = df.copy()
    df['svg'] = df.apply(lambda row: fen_to_svg(row['fen'], row['best_move']), axis=1)
    df = df[['svg'] + columns]
    return df.to_html(escape=False, index=False)


def get_df(years, months, shards=None):
    dfs = []
    for year in years:
        for month in months:
            for shard in itertools.count():
                path = S3_PATH.format(year=year, month=month, shard=shard)
                try:
                    df = pd.read_csv(path)
                    print(path)
                except Exception as e:
                    print(e)
                    break

                df = df.dropna(how='all')
                dfs.append(df)
    return pd.concat(dfs).reset_index(drop=True)
