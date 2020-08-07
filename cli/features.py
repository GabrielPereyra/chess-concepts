import click
import features


# TODO: get this directly from features model by inspecting classes.
feature_sets = {
    "base": ["elo", "best_mate", "best_score2"],
    "board": features.Board.feature_names(),
    "piece_count": features.PieceCount.feature_names(),
    "best_move": features.BestMove.feature_names(),
    "best_pv": features.BestPV.feature_names(),
}


@click.group()
def cli():
    pass


@cli.command()
@click.option("--group", default=None)
def list(group):
    """
    Prints available feature names.

    group: name of the group of features to print (e.g. board, or None to print features for all feature groups)
    """
    for group_name, feature_names in feature_sets.items():
        if group is None or group_name == group:
            print("{}:".format(group_name))
            for feature_name in feature_names:
                print("\t{}".format(feature_name))


if __name__ == "__main__":
    cli()
