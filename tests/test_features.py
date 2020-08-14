import pytest
import chess
import chess.engine
import features
import pandas as pd
from features.stockfish import STOCKFISH_PATH
import subprocess


def test_board_features():
    f = features.Board(chess.STARTING_FEN)
    assert f.features() == {
        "fullmove_number": 1,
        "is_check": False,
        "our_number_of_bishop_moves": 0,
        "our_number_of_captures": 0,
        "our_number_of_checks": 0,
        "our_number_of_knight_moves": 4,
        "our_number_of_moves": 20,
        "our_number_of_pawn_moves": 16,
        "our_number_of_queen_moves": 0,
        "our_number_of_rook_moves": 0,
        "their_number_of_bishop_moves": 0,
        "their_number_of_captures": 0,
        "their_number_of_checks": 0,
        "their_number_of_knight_moves": 4,
        "their_number_of_moves": 20,
        "their_number_of_pawn_moves": 16,
        "their_number_of_queen_moves": 0,
        "their_number_of_rook_moves": 0,
        "turn": True,
        "material_advantage": 0,
        "our_bishops": 2,
        "our_knights": 2,
        "our_pawns": 8,
        "our_piece_count": 16,
        "our_queens": 1,
        "our_rooks": 2,
        "piece_count": 32,
        "their_bishops": 2,
        "their_knights": 2,
        "their_pawns": 8,
        "their_piece_count": 16,
        "their_queens": 1,
        "their_rooks": 2,
        "is_opening": True,
        "is_endgame": False,
        "is_midgame": False,
    }


# TODO: Fix this.
@pytest.mark.xfail
def test_best_move_features():
    f = features.BestMove(chess.STARTING_FEN, "e2e4")
    assert f.features() == {
        "best_move_is_attacked": False,
        "best_move_is_capture": False,
        "best_move_is_check": False,
        "best_move_is_defended": False,
        "best_move_is_en_passant": False,
        "best_move_is_promotion": False,
        "best_move_piece_type": 1,
    }


def test_best_pv_features():
    f = features.BestPV(
        chess.STARTING_FEN,
        "['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5', 'a7a6', 'b5c6', 'd7c6']",
    )
    assert f.features() == {
        "best_pv_our_number_of_captures": 1,
        "best_pv_our_number_of_checks": 0,
        "best_pv_our_number_of_pieces_moved": 3,
        "best_pv_their_number_of_captures": 1,
        "best_pv_their_number_of_checks": 0,
        "best_pv_their_number_of_pieces_moved": 4,
    }


@pytest.mark.parametrize(
    "fen, pv, expected",
    [
        # https://www.chessgames.com/perl/chessgame?gid=1124489
        (
            "4r1k1/2pRP1pp/2p5/p4pN1/5Qn1/q5P1/P3PP1P/6K1 w - - 0 1",
            "['f4c4', 'g8h8', 'g5f7', 'h8g8', 'f7h6', 'g8h8', 'c4g8', 'e8g8', 'h6f7']",
            True,
        ),
        # https://lichess.org/analysis/rnbq1r1k/ppp1npp1/4p3/b2pP1N1/3P4/2P5/PP3PPP/RNBQK2R_w_KQ_-_0_1
        (
            "rnbq1r1k/ppp1npp1/4p3/b2pP1N1/3P4/2P5/PP3PPP/RNBQK2R w KQ - 2 9",
            "['d1h5', 'h8g8', 'h5h7']",
            False,
        ),
    ],
)
def test_smothered_mate(fen, pv, expected):
    f = features.CheckmateType(fen, pv)
    assert f.features()["is_smothered_mate"] == expected


@pytest.mark.parametrize(
    "fen, pv, expected",
    [
        # https://lichess.org/analysis/6k1/5ppp/8/8/8/8/5PPP/3R2K1_w_-_-_0_1
        ("6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1", "['d1d8']", True,),
        # https://lichess.org/analysis/8/1p2Q3/8/8/k1K5/8/8/8_w_-_-_0_1
        ("8/1p2Q3/8/8/k1K5/8/8/8 w - - 0 1", "['e7b4']", False,),
        # https://lichess.org/analysis/3r2k1/5ppp/8/8/8/8/5PPP/6K1_b_-_-_0_1
        ("3r2k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1", "['d8d1']", True,),
        # https://lichess.org/analysis/8/1P2q3/8/8/K1k5/8/8/8_b_-_-_0_1
        ("8/1P2q3/8/8/K1k5/8/8/8 b - - 0 1", "['e7b4']", False,),
    ],
)
def test_back_rank_mate(fen, pv, expected):
    f = features.CheckmateType(fen, pv)
    assert f.features()["is_back_rank_mate"] == expected


@pytest.mark.parametrize(
    "fen, pv, expected_contains_fork, expected_is_first_move_fork",
    [
        # First move is a simple knight fork
        # https://lichess.org/analysis/3k4/N3q3/8/8/8/8/8/3K4_w_-_-_0_1
        ("3k4/N3q3/8/8/8/8/8/3K4 w - - 0 1", "['a7c6', 'd8e8', 'c6e7']", True, True,),
        # First move is a double attack with queen on king and knight
        # https://lichess.org/analysis/rnbqkb1r/pp2pppp/3p4/3P4/4n3/8/PP3PPP/RNBQKBNR_w_KQkq_-_0_1
        (
            "rnbqkb1r/pp2pppp/3p4/3P4/4n3/8/PP3PPP/RNBQKBNR w KQkq - 0 1",
            "['d1a4', 'b8d7', 'a4e4']",
            True,
            True,
        ),
        # Our first move is not a fork, but our second move is knight fork, from FIDE WCC 2004
        # https://lichess.org/analysis/r5k1/1p1q1pbp/6p1/2Pp4/p3nQ2/P4P2/B2B2PP/2R4K_b_-_-_0_1
        (
            "r5k1/1p1q1pbp/6p1/2Pp4/p3nQ2/P4P2/B2B2PP/2R4K b - - 0 1",
            "['e4f2', 'h1g1', 'f2d3', 'f4e3', 'd3c1']",
            True,
            False,
        ),
        # Known opening fork after capture
        # https://lichess.org/analysis/r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R_b_KQkq_-_0_1
        (
            "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R b KQkq - 0 1",
            "['f6e4', 'c3e4', 'd7d5', 'c4d3', 'd5e4']",
            True,
            False,
        ),
        # Starting position with some example line
        # https://lichess.org/analysis/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR_w_KQkq_-_0_1
        (
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "['d2d4', 'd7d5', 'c2c4', 'e7e6', 'b1c3']",
            False,
            False,
        ),
        # First move forks the pieces but the second move is mate instead of a capture of one of forked pieces
        # https://lichess.org/analysis/6kq/8/8/4n3/4p3/8/5P2/4RBK1_b_-_-_0_1
        (
            "6kq/8/8/4n3/4p3/8/5P2/4RBK1 b - - 0 1",
            "['e4f3', 'g1g2', 'h8h2']",
            False,
            False,
        ),
    ],
)
def test_forks(fen, pv, expected_contains_fork, expected_is_first_move_fork):
    f = features.Motives(fen, pv)
    assert f.features()["contains_fork"] == expected_contains_fork
    assert f.features()["is_first_move_fork"] == expected_is_first_move_fork


@pytest.mark.parametrize(
    "fen, pv, expected",
    [
        # https://lichess.org/analysis/6kq/8/8/4n3/4p3/8/5P2/4RBK1_b_-_-_0_1
        ("6kq/8/8/4n3/4p3/8/5P2/4RBK1 b - - 0 1", "['e5f3', 'g1g2', 'h8h2']", True,),
        # https://lichess.org/analysis/8/8/8/8/1N3K1k/8/8/3Q4_w_-_-_0_1
        ("8/8/8/8/1N3K1k/8/8/3Q4 w - - 0 1", "['d1h1']", False,),
    ],
)
def test_mate_with_moved_knight_queen(fen, pv, expected):
    f = features.CheckmateType(fen, pv)
    assert f.features()["mate_with_moved_knight_queen"] == expected


def test_from_df():
    df = pd.DataFrame(
        [
            {
                "fen": chess.STARTING_FEN,
                "best_move": "e2e4",
                "best_pv": "['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5', 'a7a6', 'b5c6', 'd7c6']",
            }
        ]
    )

    for feature_class in [
        features.Board,
        features.BestMove,
        features.BestPV,
    ]:
        feature_df = feature_class.from_df(df)


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


def test_clock_features():
    f = features.Clock("60+1", 30)
    assert f.features() == {
        "approximate_game_length": 100,
        "relative_time_remaining": 0.3,
    }


def test_stockfish_depth_features():
    p = subprocess.Popen(
        STOCKFISH_PATH,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    p.stdout.readline() # read info line on init.

    f = features.StockfishDepth(chess.STARTING_FEN, p)

    p.kill()

    assert f.features() == {'mates': [None, None, None, None, None, None, None, None, None, None], 'moves': ['e2e3', 'e2e3', 'e2e3', 'd2d4', 'd2d4', 'e2e4', 'b1c3', 'b1c3', 'b1c3', 'b1c3'], 'pvs': ["['e2e3']", "['e2e3', 'b7b6']", "['e2e3', 'b7b6', 'f1c4']", "['d2d4', 'e7e6', 'e2e3', 'd7d5']", "['d2d4', 'e7e6', 'e2e3', 'd7d5']", "['e2e4', 'b7b6']", "['b1c3', 'd7d5', 'd2d4', 'c7c6', 'd1d3', 'e7e6', 'e2e4', 'd5e4']", "['b1c3', 'd7d5', 'g1f3', 'd5d4', 'c3b5', 'b8c6', 'e2e3', 'd4e3', 'd2e3', 'd8d1', 'e1d1']", "['b1c3', 'd7d5', 'd2d4', 'e7e5', 'e2e4', 'd5e4', 'c1e3', 'b8c6', 'd4e5']", "['b1c3', 'd7d5', 'd2d4', 'c7c6', 'c1f4', 'e7e6', 'e2e3']"], 'scores': [110, 122, 119, 59, 75, 172, 77, 82, 77, 115]}