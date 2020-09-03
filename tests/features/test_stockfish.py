import subprocess
import chess
import chess.engine
import features
from features.stockfish import STOCKFISH_PATH


def test_stockfish_features():
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    f = features.Stockfish10(chess.STARTING_FEN, engine)
    assert f.features() == {
        "best_mate": None,
        "best_move": "b1c3",
        "best_pv": "['b1c3', 'd7d5', 'd2d4', 'c7c6', 'c1f4', 'e7e6', 'e2e3']",
        "best_score": 115,
    }

    engine.quit()


def test_stockfish_depth_features():
    p = subprocess.Popen(
        STOCKFISH_PATH,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )
    p.stdout.readline()  # read info line on init.

    f = features.StockfishDepth(chess.STARTING_FEN, p)

    p.kill()

    assert f.features() == {
        "mates": [None, None, None, None, None, None, None, None, None, None],
        "moves": [
            "e2e3",
            "e2e3",
            "e2e3",
            "d2d4",
            "d2d4",
            "e2e4",
            "b1c3",
            "b1c3",
            "b1c3",
            "b1c3",
        ],
        "pvs": [
            "['e2e3']",
            "['e2e3', 'b7b6']",
            "['e2e3', 'b7b6', 'f1c4']",
            "['d2d4', 'e7e6', 'e2e3', 'd7d5']",
            "['d2d4', 'e7e6', 'e2e3', 'd7d5']",
            "['e2e4', 'b7b6']",
            "['b1c3', 'd7d5', 'd2d4', 'c7c6', 'd1d3', 'e7e6', 'e2e4', 'd5e4']",
            "['b1c3', 'd7d5', 'g1f3', 'd5d4', 'c3b5', 'b8c6', 'e2e3', 'd4e3', 'd2e3', 'd8d1', 'e1d1']",
            "['b1c3', 'd7d5', 'd2d4', 'e7e5', 'e2e4', 'd5e4', 'c1e3', 'b8c6', 'd4e5']",
            "['b1c3', 'd7d5', 'd2d4', 'c7c6', 'c1f4', 'e7e6', 'e2e3']",
        ],
        "scores": [110, 122, 119, 59, 75, 172, 77, 82, 77, 115],
    }


def test_stockfish_eval_features():
    p = subprocess.Popen(
        STOCKFISH_PATH,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )
    p.stdout.readline()  # read info line on init.

    f = features.StockfishEval(chess.STARTING_FEN, p)

    p.kill()

    assert f.features() == {
        "our_bishops_eg": -0.36,
        "our_bishops_mg": -0.03,
        "our_imbalance_eg": None,
        "our_imbalance_mg": None,
        "our_initiative_eg": None,
        "our_initiative_mg": None,
        "our_king safety_eg": -0.05,
        "our_king safety_mg": 0.78,
        "our_knights_eg": -0.18,
        "our_knights_mg": -0.02,
        "our_material_eg": None,
        "our_material_mg": None,
        "our_mobility_eg": -1.09,
        "our_mobility_mg": -0.82,
        "our_passed_eg": 0.0,
        "our_passed_mg": 0.0,
        "our_pawns_eg": -0.11,
        "our_pawns_mg": 0.53,
        "our_queens_eg": 0.0,
        "our_queens_mg": 0.0,
        "our_rooks_eg": -0.06,
        "our_rooks_mg": -0.26,
        "our_space_eg": 0.0,
        "our_space_mg": 0.39,
        "our_threats_eg": 0.0,
        "our_threats_mg": 0.0,
        "their_bishops_eg": -0.36,
        "their_bishops_mg": -0.03,
        "their_imbalance_eg": None,
        "their_imbalance_mg": None,
        "their_initiative_eg": None,
        "their_initiative_mg": None,
        "their_king safety_eg": -0.05,
        "their_king safety_mg": 0.78,
        "their_knights_eg": -0.18,
        "their_knights_mg": -0.02,
        "their_material_eg": None,
        "their_material_mg": None,
        "their_mobility_eg": -1.09,
        "their_mobility_mg": -0.82,
        "their_passed_eg": 0.0,
        "their_passed_mg": 0.0,
        "their_pawns_eg": -0.11,
        "their_pawns_mg": 0.53,
        "their_queens_eg": 0.0,
        "their_queens_mg": 0.0,
        "their_rooks_eg": -0.06,
        "their_rooks_mg": -0.26,
        "their_space_eg": 0.0,
        "their_space_mg": 0.39,
        "their_threats_eg": 0.0,
        "their_threats_mg": 0.0,
        "total_bishops_eg": 0.0,
        "total_bishops_mg": 0.0,
        "total_imbalance_eg": 0.0,
        "total_imbalance_mg": 0.0,
        "total_initiative_eg": 0.0,
        "total_initiative_mg": 0.0,
        "total_king safety_eg": 0.0,
        "total_king safety_mg": 0.0,
        "total_knights_eg": 0.0,
        "total_knights_mg": 0.0,
        "total_material_eg": 0.0,
        "total_material_mg": 0.0,
        "total_mobility_eg": 0.0,
        "total_mobility_mg": 0.0,
        "total_passed_eg": 0.0,
        "total_passed_mg": 0.0,
        "total_pawns_eg": 0.0,
        "total_pawns_mg": 0.0,
        "total_queens_eg": 0.0,
        "total_queens_mg": 0.0,
        "total_rooks_eg": 0.0,
        "total_rooks_mg": 0.0,
        "total_space_eg": 0.0,
        "total_space_mg": 0.0,
        "total_threats_eg": 0.0,
        "total_threats_mg": 0.0,
    }
