import os
import features
import pandas as pd

LICHESS_CSV_PATH = "csvs/lichess/{year}-{month:0>2}/"
FEATURE_CSV_PATH = "csvs/{feature_name}/{year}-{month:0>2}/"
CSV_PATH = "csvs/{type}/{year}-{month:0>2}/"


def get_type_df(type="lichess", years=[0], months=[0], shards=None):
    dfs = []
    for year in years:
        for month in months:
            path = CSV_PATH.format(type=type, year=year, month=month)
            if shards is None:
                shards = range(len(os.listdir(path)))
            for shard in shards:
                df = pd.read_csv(path + str(shard) + ".csv")
                dfs.append(df)
    return pd.concat(dfs).reset_index(drop=True)


# TODO: option to grab all types.
def get_df(types=None, years=[0], months=[0], shards=None):
    df = None
    for type in types:
        type_df = get_type_df(type, years, months, shards)
        if df is None:
            df = type_df
        else:
            assert len(df) == len(type_df)  # TODO: check indices match?
            df = df.join(type_df)
    return df
