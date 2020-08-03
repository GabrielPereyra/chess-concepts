import chess
import chess.svg
import itertools
import pandas as pd
S3_PATH = 's3://chess-puzzles/single-best-mate/{year}-{month:0>2}/{shard}.csv'


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
