import chess
import subprocess
from features.ethereal import ETHEREAL_PATH, EtherealEval


def test_stockfish_eval_features():
    p = subprocess.Popen(
        ETHEREAL_PATH,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )

    f = EtherealEval(chess.STARTING_FEN, p)

    p.kill()

    assert f.features() == {
        "our_isolated_pawns": 0,
        "their_isolated_pawns": 0,
        "our_bishop_rammed_pawns": 0,
        "their_bishop_rammed_pawns": 0,
        "our_bishops_behind_pawn": 2,
        "their_bishops_behind_pawn": 2,
        "our_bishop_long_diagonal": 0,
        "their_bishop_long_diagonal": 0,
        "our_rooks_on_seventh": 0,
        "their_rooks_on_seventh": 0,
        "our_queen_relative_pin": 0,
        "their_queen_relative_pin": 0,
    }
