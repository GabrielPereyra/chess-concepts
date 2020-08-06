import os
import pandas as pd
LICHESS_CSV_PATH = 'csvs/lichess/{year}-{month:0>2}/'
FEATURE_CSV_PATH = 'csvs/{feature_name}/{year}-{month:0>2}/'


def get_df(years=[2013], months=[1], shards=None):
    PATH = LICHESS_CSV_PATH

    dfs = []
    for year in years:
        for month in months:
            path = PATH.format(year=year, month=month)
            if shards is None:
                shards = range(len(os.listdir(path)))
            for shard in shards:
                df = pd.read_csv(path + str(shard) + '.csv')
                dfs.append(df)
    return pd.concat(dfs).reset_index(drop=True)
