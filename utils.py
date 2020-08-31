import os
import features
import pandas as pd


CSV_PATH = "csvs/{type}/{name}/"


def get_type_df(name, type, shard, num_shards=None):
    path = CSV_PATH.format(type=type, name=name)
    if shard:
        shards = [shard]
    if num_shards is None:
        shards = range(len(os.listdir(path)))
    else:
        shards = range(num_shards)

    dfs = []
    for shard in shards:
        df = pd.read_csv(path + str(shard) + ".csv")
        dfs.append(df)

    return pd.concat(dfs).reset_index(drop=True)


def get_df(name, types, shard=None, num_shards=None):
    df = None
    for type in types:
        type_df = get_type_df(name, type, shard, num_shards)
        if df is None:
            df = type_df
        else:
            assert len(df) == len(type_df)  # TODO: check indices match?
            df = df.join(type_df)
    return df