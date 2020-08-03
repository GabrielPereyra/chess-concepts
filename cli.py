import utils
import click
import features
import pandas as pd

# TODO: move this to model file?
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression


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

    df = pd.read_csv('data.csv')

    columns = []
    for feature_set in feature_set_list:
        columns.extend(getattr(feature_sets, feature_set))

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
def difficulty():
    """
    Train a model to predict blunders and add this to csvs/data.csv as a feature column.
    """

    df = pd.read_csv('data.csv')

    columns = []
    feature_set_list = ['base', 'board', 'piece_count']
    for feature_set in feature_set_list:
        columns.extend(getattr(feature_sets, feature_set))

    x = df[columns].values
    y = df['correct']

    x = StandardScaler().fit_transform(x)

    model = LogisticRegression().fit(x, y)

    test_df = df.copy()
    test_df['elo'] = df['elo'].mean()
    x = df[columns].values
    x = StandardScaler().fit_transform(x)

    difficulty = model.predict_proba(x)[:, 0]
    df['difficulty'] = difficulty

    df.to_csv('data.csv', index=False)


if __name__ == '__main__':
    cli()
