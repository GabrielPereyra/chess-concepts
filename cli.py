import os
import utils
import click
import features
PGN_PATH = 'pgns/{}.pgn'
CSV_PATH = 'csvs/{}.csv'
os.makedirs("csvs", exist_ok=True)


@click.command()
@click.argument("name")
@click.argument("feature-names", nargs=-1)
def csv(name, feature_names):
    pgn = open(PGN_PATH.format(name))
    feature_classes = [getattr(features, name) for name in feature_names]
    df = utils.pgn_to_feature_df(pgn, feature_classes)
    df.to_csv(CSV_PATH.format(name), index=False)