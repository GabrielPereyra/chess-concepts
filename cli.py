import os
import utils
import click
import features
import pandas as pd

PGN_PATH = "pgns/{}.pgn"
os.makedirs("csvs", exist_ok=True)


@click.command()
@click.argument("pgn-path")
@click.argument("feature-names", nargs=-1)
@click.option("--limit", type=int, default=1e9)
@click.option("--cache", is_flag=True)
def csv(pgn_path, feature_names, limit, cache):
    csv_path = pgn_path.replace("pgn", "csv")
    if limit:
        csv_path = csv_path.replace(".csv", "_{}.csv".format(limit))

    if cache:
        df = pd.read_csv(csv_path)
    else:
        pgn = open(pgn_path)
        df = utils.pgn_to_df(pgn, limit)

    feature_classes = [getattr(features, name) for name in feature_names]
    df = utils.add_features(df, feature_classes)

    df.to_csv(csv_path, index=False)
