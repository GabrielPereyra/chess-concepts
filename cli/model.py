import utils
import click
import features
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

BINARY_METRICS = [
    "is_correct",
    "is_blunder",
    "is_mistake",
    "is_inaccurate",
    "into_mate",
    "lost_mate",
]

METRICS = BINARY_METRICS + [
    "score_loss",
    "mate_loss",
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
    "score",
    "mate",
    "prev_score",
    "prev_mate",
    "clock",
]


def print_feature_importance(coef, feature_names):
    df = pd.DataFrame({"importance": map(abs, coef), "feature": feature_names})
    df = df.sort_values("importance", ascending=False)
    print("Feature Importance")
    print(df)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("year")
@click.argument("month")
@click.argument("metric", type=click.Choice(METRICS, case_sensitive=False))
@click.option("--num_shards", type=int, help="number of shards to use.")
@click.option("csvs", "--csv", multiple=True, default=["lichess"], help="Csvs to load.")
@click.option("--importance", is_flag=True, help="Print feature importance.")
def sklearn(year, month, metric, num_shards, csvs, importance):
    """
    Train dummy and logistic regression models to predict a given metric.
    """
    df = utils.get_df(csvs, years=[year], months=[month], num_shards=num_shards)

    # balance
    if metric in BINARY_METRICS:
        limit = min(len(df[df[metric]]), len(df[~df[metric]]))
        df = pd.concat([df[df[metric]][:limit], df[~df[metric]][:limit]])

    print("using {} examples".format(len(df)))

    # remove games without time_control.
    if "approximate_game_length" in df.columns:
        df = df[~df["approximate_game_length"].isna()]

    y = df[metric]
    df = df.drop(METRICS + NON_FEATURE_COLUMNS, axis=1)
    x = df[df.columns].values

    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=0)
    s = StandardScaler()
    x_train = s.fit_transform(x_train)
    x_test = s.transform(x_test)

    model = LogisticRegression()
    model = model.fit(x_train, y_train)
    print()
    print("Classification Report")
    print(classification_report(y_test, model.predict(x_test)))

    if importance:
        print_feature_importance(model.coef_[0], df.columns)


if __name__ == "__main__":
    cli()
