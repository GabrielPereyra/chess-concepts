import os
import utils
import click
import features
import pandas as pd
import plotly.express as px
import requests

# TODO: move this to model file?
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
os.makedirs('csvs', exist_ok=True)
os.makedirs('pgns', exist_ok=True)


feature_sets = {
    'base': ['elo', 'best_mate', 'best_score2'],
    'board': features.Board.feature_names(),
    'piece_count': features.PieceCount.feature_names(),
    'best_move': features.BestMove.feature_names(),
    'best_pv': features.BestPV.feature_names(),
}


@click.group()
def cli():
    pass


@cli.command()
@click.argument('years')
@click.argument('months')
@click.argument('feature_names', nargs=-1)
def csv(years, months, feature_names):
    """
    Generate feature table (csvs/data.csv) which is used by boards visualization tool (notebooks/boards.ipynb) and models (cli model).

    years: Comma-separated list of years (e.g. 2013,2014)

    months: Comma-separated list of years (e.g. 1,2)

    feature_names: Feature classes (e.g. Board Mate ...)

    """
    df = utils.get_df(years.split(','), months.split(','))

    for feature_name in feature_names:
        print(feature_name)
        feature_class = getattr(features, feature_name)
        feature_df = feature_class.from_df(df)
        df = df.join(feature_df)

    df.to_csv('csvs/data.csv', index=False)


@cli.command()
@click.argument('feature_set_list', nargs=-1)
def model(feature_set_list):
    """
    Train dummy and logistic regression models to predict probability of a blunder on positions where there is a single best mate. Uses csvs/data,csv as input (need to generate this using cli csv first).
    """

    df = pd.read_csv('csvs/data.csv')

    # TODO: move this into models.

    columns = []
    for feature_set in feature_set_list:
        columns.extend(feature_sets[feature_set])

    x = df[columns].values
    y = df['correct']

    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=0)
    s = StandardScaler()
    x_train = s.fit_transform(x_train)
    x_test = s.transform(x_test)

    models = [
        DummyClassifier(strategy='most_frequent'),
        LogisticRegression(),
    ]

    for model in models:
        score = model.fit(x_train, y_train).score(x_test, y_test)
        print('{:.0%}'.format(score))


@cli.command()
@click.argument('feature')
@click.option('--elo_bin', default=200)
def plot(feature, elo_bin):
    """
    Create a plotly plot of feature vs. accuracy by elo. Assumes you have created csvs/data.csv and the feature exists as a column.
    """

    df = pd.read_csv('csvs/data.csv')

    # TODO: generalize this to remove feature values with low counts.
    if feature == 'best_mate':
        df = df[df[feature] < 10]

    df = df[df['elo'] > 800]
    df = df[df['elo'] < 2200]


    df['elo'] = df['elo'].apply(lambda elo: int(elo / elo_bin) * elo_bin)
    df = df.groupby([feature, 'elo'], as_index=False).mean()

    fig = px.line(
        df,
        x='elo',
        y='correct',
        color=feature
    )

    fig.show()


@cli.command()
@click.argument('username')
def user_pgn(username):
    """Download {username} games from lichess.org. Note: we only download games that have been analyzed."""
    r = requests.get('https://lichess.org/api/games/user/{username}?analysed=1&evals=1&perfType=ultraBullet,bullet,blitz,rapid,classical&clocks=1&opening=1'.format(username=username))

    with open('pgns/{}.pgn'.format(username), 'w') as f:
        f.write(r.text)


@cli.command()
@click.argument('username')
def user_csv(username):
    """Convert lichess user pgn to csv."""
    pgn_path = 'pgns/{}.pgn'.format(username)
    df = utils.user_df(pgn_path)
    df.to_csv('csvs/{}.csv'.format(username))


if __name__ == '__main__':
    cli()
