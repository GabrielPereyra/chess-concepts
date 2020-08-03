import pandas as pd
import xgboost as xgb
import feature_sets
from sklearn.model_selection import train_test_split
from sklearn.metrics.classification import accuracy_score

df = pd.read_csv('data.csv')
print(len(df))
print(df.columns)


feature_set_list = ['base', 'board', 'piece_count', 'best_move', 'best_pv', 'their_king']
columns = []
for feature_set in feature_set_list:
    columns.extend(getattr(feature_sets, feature_set))

x = df[columns].values
y = df['correct']
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=0)

dtrain = xgb.DMatrix(x_train, label=y_train)
dtest = xgb.DMatrix(x_test, label=y_test)

param = {
    # 'gamma': 1,
    # 'lambda': 5,
    # 'alpha': 2,
    # 'min_child_weight': 100,
    # 'max_depth': 3,
    # 'eta': 5,
    'objective':'binary:logistic',
    'nthread': 8,
    'tree_method': 'hist',
    # 'subsample': 0.9,
    # 'num_parallel_tree': 2,
    # 'colsample_bytree': 0.9,
    # 'colsample_bylevel': 0.9,
    # 'colsample_bynode': 0.9,
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
