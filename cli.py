import utils
import click
import features
import pandas as pd


@click.group()
def cli():
    pass


@cli.command()
def list():
    for feature in dir(features):
        if 'Features' in feature:
            print(feature)
            feature_class = getattr(features, feature)
            for feature_name in features.class_features(feature_class):
                print('\t', feature_name)


@cli.command()
@click.argument('years')
@click.argument('months')
@click.argument('feature_names', nargs=-1)
def csv(years, months, feature_names):
    df = utils.get_df(years.split(','), months.split(','))

    for feature_name in feature_names:
        print(feature_name)
        feature_class = getattr(features, feature_name)
        feature_df = feature_class.from_df(df)
        df = df.join(feature_df)

    df.to_csv('data.csv', index=False)


@cli.command()
@click.argument('feature_set_list', nargs=-1)
def model(feature_set_list):
    import feature_sets
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.dummy import DummyClassifier
    from sklearn.linear_model import LogisticRegression

    df = pd.read_csv('data.csv')

    print(len(df))
    print(df.columns)

    columns = []
    for feature_set in feature_set_list:
        columns.extend(getattr(feature_sets, feature_set))

    # TODO: how to do feature sets?
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


if __name__ == '__main__':
    cli()
