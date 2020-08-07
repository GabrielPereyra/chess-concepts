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

Preprocessed game data from lichess.org is hosted on aws [here](https://s3.console.aws.amazon.com/s3/buckets/chess-puzzles) (I'll add the code for generating these to this repo soon). The buckets are public so you shouldn't need any credentials to download them, but let me know if that doesn't work for some reason.
