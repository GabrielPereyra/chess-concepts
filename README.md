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

```
# to see options
cli

# generate features table using lichess 2013-01 data.
cli csv 2013 1 Board PieceCount BestMove BestPV Checkmate

# train a model to predict blunders using csv data.
cli model

# plot elo vs. accuracy by mate depth.
cli plot best_mate
```
# Notebooks

| Notebook | Description |
|--------- | ----------- |
| [boards](./widgets/boards.ipynb) | Visualize boards based on features. |

# Todo

* Add all [checkmate patterns](https://en.wikipedia.org/wiki/Checkmate_pattern) to Checkmate class in `features.py`.

# Data

Preprocessed game data from lichess.org is hosted on aws [here](https://s3.console.aws.amazon.com/s3/buckets/chess-puzzles) (I'll add the code for generating these to this repo soon). The buckets are public so you shouldn't need any credentials to download them, but let me know if that doesn't work for some reason.
