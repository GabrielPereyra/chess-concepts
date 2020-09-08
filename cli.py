import os
import utils
import click
import features
PGN_PATH = 'pgns/{}.pgn'
CSV_PATH = 'csvs/{}.csv'
os.makedirs("csvs", exist_ok=True)


# TODO: limit feature.
# TODO: add cache option (reuse existing csv instead of creating new one and only overwrite features passsed in).
@click.command()
@click.argument("name")
@click.argument("feature-names", nargs=-1)
@click.option("--limit", type=int)
def csv(name, feature_names, limit):
    pgn = open(PGN_PATH.format(name))
    feature_classes = [getattr(features, name) for name in feature_names]
    df = utils.pgn_to_df(pgn, limit)
    df = utils.add_features(df, feature_classes)
    if limit:
        name += '_{}'.format(limit)
    df.to_csv(CSV_PATH.format(name), index=False)