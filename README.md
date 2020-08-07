# Chess Features

Code for generating features from chess positions, training models to predict blunders from these features and visualization tools.

# Setup

```
git clone https://github.com/GabrielPereyra/chess-features
cd chess-features

virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
pip install --editable .
```

# Command line

These commands expect certain csvs to exists before they are run (see data for steps to create these csvs).

Make sure to run `pip install --editable .`!

## CSV
```
# generate lichess csv from pgn (make sure to download lichess pgn from https://database.lichess.org/ and put it in pgns/)
csv lichess year month

# generate feature csv from lichess csv (make sure to create lichess csv first.)
csv feature year month feature_name
```

## Features
```
# list features grouped by class.
features list
```

## Plot
```
# Plotly elo histogram with test pgn.
plot hist 0 0 1 elo
```

# Development

## Testing

```
# run pytest with code coverage
coverage run -m pytest

# print code coverage report
coverage report
```

## Linting
```
black .
```

# Data

## Create test csvs
```
# create lichess csv.
csv lichess 0 0

# create feature csvs (make sure to capitalize class name!).
csv feature 0 0 Board
csv feature 0 0 PieceCount
csv feature 0 0 Stockfish10
```

## Create csvs
```
# Get lichess.org games from the month of 2015-12.
wget --directory pgns https://database.lichess.org/standard/lichess_db_standard_rated_2015-12.pgn.bz2

# create lichess csv.
csv lichess 2015 12

# create feature csvs (make sure to capitalize class name!).
csv feature 2015 12 Board
csv feature 2015 12 PieceCount
csv feature 2015 12 Stockfish10
```

## Download csvs
- [ ] Add csvs to [s3 bucket](https://s3.console.aws.amazon.com/s3/buckets/chess-puzzles)
- [ ] Add script to download csvs from aws.