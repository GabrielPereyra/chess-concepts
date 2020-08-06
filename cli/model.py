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


@csv.command()
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
