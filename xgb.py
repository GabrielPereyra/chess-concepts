import pandas as pd
import xgboost as xgb
import feature_sets
from sklearn.model_selection import train_test_split
from sklearn.metrics.classification import accuracy_score


def get_data():
    df = pd.read_csv('data.csv')
    # df = df[df['best_score2'] < 4000]
    # df = df[df['best_score2'] > -2000]

    # df = df[df['best_mate'] == 1]
    # df = df[df['elo'] < 1600]
    # df = df[df['elo'] >= 1500]


    # balance
    # incorrect_df = df[~df['correct']]
    # correct_df = df[df['correct']]
    # min_len = min(len(incorrect_df), len(correct_df))
    # df = pd.concat([incorrect_df[:min_len], correct_df[:min_len]])

    feature_set_list = ['base', 'board', 'piece_count']
    columns = []
    for feature_set in feature_set_list:
        columns.extend(getattr(feature_sets, feature_set))

    print(len(df))
    print(df.columns)

    x = df[columns].values
    y = df['correct']
    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=0)

    dtrain = xgb.DMatrix(x_train, label=y_train)
    dtest = xgb.DMatrix(x_test, label=y_test)
    return dtrain, dtest


if __name__ == '__main__':

    param = {
        'objective':'binary:logistic',
        'nthread': 8,
        'tree_method': 'hist',
        # 'num_parallel_tree': 100,
        # 'min_child_weight': 100,
        # 'gamma': 1,
        # 'lambda': 2,
        # 'alpha': 2,
        # 'max_depth': 3,
        # 'eta': 5,
        # 'subsample': 0.8,
        # 'colsample_bytree': 0.8,
        # 'colsample_bylevel': 0.8,
        # 'colsample_bynode': 0.8,
    }

    bst = xgb.train(
        param,
        dtrain,
        1000,
        evals=[
            (dtrain, 'train'),
            (dtest, 'test')
        ],
        early_stopping_rounds=10,
    )

    y_pred = bst.predict(dtest, ntree_limit=bst.best_ntree_limit)
    y_pred = y_pred > 0.5
    print(accuracy_score(y_test, y_pred))

    bst.save_model('xgb_checkpoint.json')

    # TODO: combine this all into one df.
    # bst.feature_names = columns
    # for importance_type in ['weight', 'gain', 'cover', 'total_gain', 'total_cover']:
    #     print(pd.DataFrame(bst.get_score(importance_type=importance_type).items(), columns=['feature', importance_type]).sort_values(importance_type, ascending=False))
