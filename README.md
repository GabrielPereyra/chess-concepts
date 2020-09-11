# Chess Concepts

Extract chess concepts from positions.

```python
import chess
import features

# Board features
features.Board(chess.STARTING_FEN).our_number_of_moves
features.Board(chess.STARTING_FEN).our_queens
features.Board(chess.STARTING_FEN).our_bishop_pair
features.Board(chess.STARTING_FEN).material_advantage
features.Board(chess.STARTING_FEN).position_openness

# Move features
features.BestMove(chess.STARTING_FEN, 'e2e4').best_move_tactic
features.BestMove(chess.STARTING_FEN, 'e2e4').best_move_piece_type
```

# Annotate PGNs

Create a csv file where each row is a position from a game containing player meta data and position concepts.

```
# Annotate a pgn with board, stockfish and best move features.
csv pgns/test.pgn Board, Stockfish10, BestMove
```

# Setup

```
git clone https://github.com/GabrielPereyra/chess-concepts
cd chess-concepts

virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
pip install --editable .
```
