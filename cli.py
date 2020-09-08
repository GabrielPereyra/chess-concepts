import os
import utils
import click
import features
PGN_PATH = 'pgns/{}.pgn'
os.makedirs("csvs", exist_ok=True)


# TODO: add progress bar.
# TODO:
# TODO: add cache option (reuse existing csv instead of creating new one and only overwrite features passsed in).
@click.command()
@click.argument("pgn-path")
@click.argument("feature-names", nargs=-1)
@click.option("--limit", type=int)
def csv(pgn_path, feature_names, limit):
    pgn = open(pgn_path)
    feature_classes = [getattr(features, name) for name in feature_names]
    df = utils.pgn_to_df(pgn, limit)
    df = utils.add_features(df, feature_classes)
    csv_path = pgn_path.replace('pgn', 'csv')
    if limit:
        csv_path = csv_path.replace('.csv', '_{}.csv'.format(limit))
    df.to_csv(csv_path, index=False)