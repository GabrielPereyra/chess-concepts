import utils
import click
import features
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression

METRICS = [
    "is_correct",
    "is_blunder",
    "is_mistake",
    "is_inaccurate",
    "score_loss",
    "mate_loss",
    "into_mate",
    "lost_mate",
    "winning_chances_loss",
]

NON_FEATURE_COLUMNS = [
    "datetime",
    "username",
    "fen",
    "game_id",
    "eco",
    "move",
    "prev_move",
    "opening",
    "eco",
    "time_control",
    "winning_chances",
    # TODO: how to handle nans in these?
    "score",
    "mate",
    "prev_score",
    "prev_mate",
    "clock",
]


@click.group()
def cli():
    pass


@cli.command()
@click.argument("year")
@click.argument("month")
@click.argument("metric", type=click.Choice(METRICS, case_sensitive=False))
@click.option("--shards", type=int, help="Number of shards to use.")
@click.option("csvs", "--csv", multiple=True, default=["lichess"], help="Csvs to load.")
def sklearn(year, month, metric, shards, csvs):
    """
    Train dummy and logistic regression models to predict a given metric.
    """
    if shards is not None:
        shards = range(shards)
    df = utils.get_df(csvs, years=[year], months=[month], shards=shards)
    y = df[metric]
    df = df.drop(METRICS + NON_FEATURE_COLUMNS, axis=1)
    x = df[df.columns].values

    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=0)
    s = StandardScaler()
    x_train = s.fit_transform(x_train)
    x_test = s.transform(x_test)

    models = [
        DummyClassifier(strategy="most_frequent"),
        LogisticRegression(),
    ]

    for model in models:
        score = model.fit(x_train, y_train).score(x_test, y_test)
        print("{:.0%}".format(score))


if __name__ == "__main__":
    cli()
