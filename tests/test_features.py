import pytest
import chess
import chess.engine
import features
import pandas as pd
from features.stockfish import STOCKFISH_PATH
from features.helpers import square_from_name
from features.helpers import PositionOpenness
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


def test_best_move_features():
    move_uci = "e2e4"
    f = features.BestMove(chess.STARTING_FEN, move_uci)
    assert f.features() == {
        "best_move_is_attacked": False,
        "best_move_is_capture": False,
        "best_move_is_check": False,
        "best_move_is_defended": False,
        "best_move_is_en_passant": False,
        "best_move_is_promotion": False,
        "best_move_piece_type": 1,
        "best_move_is_backward": False,
        "best_move_is_forward": True,
        "best_move_is_horizontal": False,
        "best_move_from_square": chess.Move.from_uci(move_uci).from_square,
        "best_move_to_square": chess.Move.from_uci(move_uci).to_square,
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
        "best_pv_our_moved_piece_types": [chess.PAWN, chess.KNIGHT, chess.BISHOP],
        "best_pv_their_moved_piece_types": [chess.PAWN, chess.KNIGHT],
    }


@pytest.mark.parametrize(
    "fen, expected",
    [
        # https://lichess.org/analysis/rnbqnrk1/pp2bppp/3p4/2pPp3/2P1P3/2NBB3/PP2QPPP/R3K1NR_w_KQ_-_0_1
        (
            "rnbqnrk1/pp2bppp/3p4/2pPp3/2P1P3/2NBB3/PP2QPPP/R3K1NR w KQ - 0 1",
            set(["c4", "c5", "d5", "d6", "e4", "e5"]),
        ),
        # https://lichess.org/analysis/r5k1/pp2rppp/1n2bn2/2R5/3QPq2/P4PN1/1B2B1PP/5RK1_w_-_-_0_1
        ("r5k1/pp2rppp/1n2bn2/2R5/3QPq2/P4PN1/1B2B1PP/5RK1 w - - 0 1", set(),),
        # https://lichess.org/analysis/rn1qk2r/pb2bppp/1p1ppn2/8/2PQ4/2N2NP1/PP2PPBP/R1B2RK1_w_kq_-_0_1
        ("rn1qk2r/pb2bppp/1p1ppn2/8/2PQ4/2N2NP1/PP2PPBP/R1B2RK1 w kq - 0 1", set(),),
        # https://lichess.org/editor/rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR_w_KQkq_-_0_1
        ("rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 1", set(["d4"]),),
        # https://lichess.org/editor/rnbqkbnr/pp2pppp/2p5/2Pp4/3PP3/8/PP3PPP/RNBQKBNR_w_KQkq_-_0_1
        (
            "rnbqkbnr/pp2pppp/2p5/2Pp4/3PP3/8/PP3PPP/RNBQKBNR w KQkq - 0 1",
            set(["c5", "c6", "d4"]),
        ),
    ],
)
def test_locked_pawns(fen, expected):
    locked_pawns = features.Board._locked_pawns(fen)
    assert locked_pawns == {square_from_name(square_name) for square_name in expected}


@pytest.mark.parametrize(
    "fen, expected",
    [
        # https://lichess.org/analysis/rnbqnrk1/pp2bppp/3p4/2pPp3/2P1P3/2NBB3/PP2QPPP/R3K1NR_w_KQ_-_0_1
        (
            "rnbqnrk1/pp2bppp/3p4/2pPp3/2P1P3/2NBB3/PP2QPPP/R3K1NR w KQ - 0 1",
            PositionOpenness.CLOSED,
        ),
        # https://lichess.org/analysis/r5k1/pp2rppp/1n2bn2/2R5/3QPq2/P4PN1/1B2B1PP/5RK1_w_-_-_0_1
        (
            "r5k1/pp2rppp/1n2bn2/2R5/3QPq2/P4PN1/1B2B1PP/5RK1 w - - 0 1",
            PositionOpenness.OPEN,
        ),
        # https://lichess.org/analysis/rn1qk2r/pb2bppp/1p1ppn2/8/2PQ4/2N2NP1/PP2PPBP/R1B2RK1_w_kq_-_0_1
        (
            "rn1qk2r/pb2bppp/1p1ppn2/8/2PQ4/2N2NP1/PP2PPBP/R1B2RK1 w kq - 0 1",
            PositionOpenness.SEMI_OPEN,
        ),
        # https://lichess.org/analysis/rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR_w_KQkq_-_0_1
        (
            "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 1",
            PositionOpenness.CLOSED,
        ),
        # https://lichess.org/analysis/rnbqkbnr/pp2pppp/2p5/2Pp4/3PP3/8/PP3PPP/RNBQKBNR_w_KQkq_-_0_1
        (
            "rnbqkbnr/pp2pppp/2p5/2Pp4/3PP3/8/PP3PPP/RNBQKBNR w KQkq - 0 1",
            PositionOpenness.CLOSED,
        ),
        # https://lichess.org/analysis/fromPosition/r1b2rk1/pp2bppp/2n1pn2/q7/2B2B2/P1N1PN2/1PQ2PPP/3RK2R_b_K_-_0_12
        (
            "r1b2rk1/pp2bppp/2n1pn2/q7/2B2B2/P1N1PN2/1PQ2PPP/3RK2R b K - 0 12",
            PositionOpenness.SEMI_OPEN,
        ),
        # https://lichess.org/analysis/r1b2rk1/pp2bppp/2n1p3/q6n/2B2B2/P1N1PN2/1PQ2PPP/3RK2R_w_K_-_0_1
        (
            "r1b2rk1/pp2bppp/2n1p3/q6n/2B2B2/P1N1PN2/1PQ2PPP/3RK2R w K - 0 1",
            PositionOpenness.SEMI_OPEN,
        ),
        # https://lichess.org/analysis/fromPosition/4rr1k/n4ppp/p7/q2BPQ2/1p6/P3P3/1P3P1P/2RR2K1_b_-_-_1_25
        (
            "4rr1k/n4ppp/p7/q2BPQ2/1p6/P3P3/1P3P1P/2RR2K1 b - - 1 25",
            PositionOpenness.OPEN,
        ),
    ],
)
def test_position_openness(fen, expected):
    f = features.Board(fen)
    assert f.features()["position_openness"] == expected


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
def test_fork(fen, pv, expected_contains_fork, expected_is_first_move_fork):
    f = features.Motives(fen, pv)
    assert f.features()["contains_fork"] == expected_contains_fork
    assert f.features()["is_first_move_fork"] == expected_is_first_move_fork


@pytest.mark.parametrize(
    "fen, pv, expected_contains_discovered_attack, expected_is_first_move_discovered_attack",
    [
        # Tricky discovered attack
        # https://lichess.org/analysis/4q3/8/8/4k3/4B3/4R1r1/1K4P1/8_w_-_-_0_1
        ("4q3/8/8/4k3/4B3/4R1r1/1K4P1/8 w - - 0 1", "['e4f3']", True, True),
        # Trap in french advanced variation, discovered attack on undefended piece of same value as piece attacking it
        # https://lichess.org/analysis/r1b1kbnr/pp3ppp/4p3/3pP3/3q4/3B4/PP3PPP/RNBQK2R_w_KQkq_-_0_1
        (
            "r1b1kbnr/pp3ppp/4p3/3pP3/3q4/3B4/PP3PPP/RNBQK2R w KQkq - 0 1",
            "['d3b5']",
            True,
            True,
        ),
        # https://lichess.org/analysis/3rr1k1/pp2bpp1/2p4p/3p2q1/8/P3PPB1/1PP1QP1P/1K1R2R1_w_-_-_0_1
        (
            "3rr1k1/pp2bpp1/2p4p/3p2q1/8/P3PPB1/1PP1QP1P/1K1R2R1 w - - 0 1",
            "['g3c7']",
            True,
            True,
        ),
        # https://lichess.org/analysis/r3r1k1/pp2bpp1/2p1pn1p/8/2Pq4/2NB4/PP1Q1PPP/R3R1K1_w_-_-_0_1
        (
            "r3r1k1/pp2bpp1/2p1pn1p/8/2Pq4/2NB4/PP1Q1PPP/R3R1K1 w - - 0 1",
            "['d3h7']",
            True,
            True,
        ),
        # https://lichess.org/analysis/1r1qrbk1/1b3pp1/p1n2n1p/2p1p3/P3P3/2P2N1P/2BBQPP1/R2R1NK1_w_-_-_0_1
        (
            "1r1qrbk1/1b3pp1/p1n2n1p/2p1p3/P3P3/2P2N1P/2BBQPP1/R2R1NK1 w - - 0 1",
            "['d2h6']",
            True,
            True,
        ),
        # Double check and mate
        # https://lichess.org/analysis/5rk1/1p1q1ppp/pb3n2/2r1p1B1/4P3/1Q1P1R2/PP2N1PP/R5K1_b_-_-_0_1
        (
            "5rk1/1p1q1ppp/pb3n2/2r1p1B1/4P3/1Q1P1R2/PP2N1PP/R5K1 b - - 0 1",
            "['c5c1']",
            True,
            True,
        ),
        # Windmill
        # https://lichess.org/analysis/r3rnk1/pb3pp1/3ppB1p/7q/1P1P4/4N1R1/P4PPP/4R1K1_w_-_-_0_1
        (
            "r3rnk1/pb3pp1/3ppB1p/7q/1P1P4/4N1R1/P4PPP/4R1K1 w - - 0 1",
            "['g3g7', 'g8h8', 'g7f7', 'h8g8']",
            True,
            False,
        ),
        # Check discovering an attack on undefended bishop by a queen
        # https://lichess.org/analysis/r4r2/pbpp2bk/1p2p1p1/7p/4NB1P/qP1P1QP1/2P2P2/3RR1K1_w_-_-_0_1
        (
            "r4r2/pbpp2bk/1p2p1p1/7p/4NB1P/qP1P1QP1/2P2P2/3RR1K1 w - - 0 1",
            "['e4g5']",
            True,
            True,
        ),
        # Moving a pawn to attack a rook discovers a check by a our rook
        # https://lichess.org/analysis/6r1/5p2/r1p1p3/B3np2/RP5k/2R4P/5P2/5K2_w_-_-_0_1
        ("6r1/5p2/r1p1p3/B3np2/RP5k/2R4P/5P2/5K2 w - - 0 1", "['b4b5']", True, True,),
        # Almost like a trap in french advanced variation but discovered attack on a defended piece of the same value
        # as the attacking piece
        # https://lichess.org/analysis/r1b1kbnr/pp3ppp/4p3/2ppP3/3q4/3B4/PP3PPP/RNBQK2R_w_KQkq_-_0_1
        (
            "r1b1kbnr/pp3ppp/4p3/2ppP3/3q4/3B4/PP3PPP/RNBQK2R w KQkq - 0 1",
            "['d3b5']",
            False,
            False,
        ),
        # Moving the bishop makes results in a rook that was behind it to attack a defended pawn
        # https://lichess.org/analysis/q2rr1k1/pp2bpp1/2p4p/3p4/8/P3PPB1/1PP1QP1P/1K1R2R1_w_-_-_0_1
        (
            "q2rr1k1/pp2bpp1/2p4p/3p4/8/P3PPB1/1PP1QP1P/1K1R2R1 w - - 0 1",
            "['g3c7']",
            False,
            False,
        ),
        # Check discovering an attack on a defended bishop by a queen
        # https://lichess.org/analysis/1r3r2/pbpp2bk/1p2p1p1/7p/4NB1P/qP1P1QP1/2P2P2/3RR1K1_w_-_-_0_1
        (
            "1r3r2/pbpp2bk/1p2p1p1/7p/4NB1P/qP1P1QP1/2P2P2/3RR1K1 w - - 0 1",
            "['e4g5']",
            False,
            False,
        ),
        # Not a discovered attack because opponent can capture the uncovered attacking piece
        # https://lichess.org/analysis/6k1/5p1p/4p1p1/1p1p2P1/6P1/8/R2K2r1/8_w_-_-_0_1
        ("6k1/5p1p/4p1p1/1p1p2P1/6P1/8/R2K2r1/8 w - - 0 1", "['d2e3']", False, False,),
        # Not a discovered attack because moving the king doesn't uncover any new attacker
        # https://lichess.org/analysis/8/pp6/3kB3/5P2/7K/2P3p1/P4n2/5R2_w_-_-_0_1
        ("8/pp6/3kB3/5P2/7K/2P3p1/P4n2/5R2 w - - 0 1", "['h4g3']", False, False,),
        # Discovered attack - moving the pawn uncovers queen attacking opponent's king
        # https://lichess.org/analysis/7N/6p1/8/2k2PQ1/6P1/8/6KP/8_w_-_-_0_1
        ("7N/6p1/8/2k2PQ1/6P1/8/6KP/8 w - - 0 1", "['f5f6']", True, True,),
        # Discovered attack - moving the bishop uncovers rook attacking opponent's king
        # https://lichess.org/analysis/8/1kB4R/r7/8/2P5/7P/2K5/8_w_-_-_0_1
        ("8/1kB4R/r7/8/2P5/7P/2K5/8 w - - 0 1", "['c7e5']", True, True,),
        # Not a discovered attack because moving the rook doesn't uncover any new attacker
        # https://lichess.org/analysis/7k/1p4p1/4K3/6b1/8/2r2P2/1r4PP/8_b_-_-_0_1
        ("7k/1p4p1/4K3/6b1/8/2r2P2/1r4PP/8 b - - 0 1", "['b2b5']", False, False),
        # Not a discovered attack because moving the rook doesn't uncover any new attacker
        # https://lichess.org/analysis/7k/1p4p1/8/5Kb1/8/2r2P2/4r1PP/8_b_-_-_0_1
        ("7k/1p4p1/8/5Kb1/8/2r2P2/4r1PP/8 b - - 0 1", "['c3c5']", False, False,),
        # Discovered attack - moving the rook uncovers bishop attacking opponent's king
        # https://lichess.org/analysis/7k/1pb3p1/8/4r3/2r5/5P1P/6PK/8_b_-_-_0_1
        ("7k/1pb3p1/8/4r3/2r5/5P1P/6PK/8 b - - 0 1", "['e5e1']", True, True,),
        # Not a discovered attack because capturing the knight with check doesn't uncover any new attacker
        # https://lichess.org/analysis/8/8/8/6P1/p3kp2/P2R4/8/2r1N1K1_b_-_-_0_1
        ("8/8/8/6P1/p3kp2/P2R4/8/2r1N1K1 b - - 0 1", "['c1e1']", False, False,),
        # Discovered attack, bishop captures a pawn and discovers our rook attacking their queen
        # https://lichess.org/analysis/r2q1rk1/4p1bp/2p3p1/pp2P2n/8/2NB3Q/PPP2PP1/2KR3R_w_-_-_0_1
        (
            "r2q1rk1/4p1bp/2p3p1/pp2P2n/8/2NB3Q/PPP2PP1/2KR3R w - - 0 1",
            "['d3g6']",
            True,
            True,
        ),
    ],
)
def test_discovered_attack(
    fen,
    pv,
    expected_contains_discovered_attack,
    expected_is_first_move_discovered_attack,
):
    f = features.Motives(fen, pv)
    assert (
        f.features()["contains_discovered_attack"]
        == expected_contains_discovered_attack
    )
    assert (
        f.features()["is_first_move_discovered_attack"]
        == expected_is_first_move_discovered_attack
    )


@pytest.mark.parametrize(
    "fen, pv, expected_contains_skewer, expected_is_first_move_skewer",
    [
        # https://lichess.org/analysis/8/3qk3/4b3/8/4KR2/5Q2/8/8_b_-_-_0_1
        ("8/3qk3/4b3/8/4KR2/5Q2/8/8 b - - 0 1", "['e6d5']", True, True,),
        # https://lichess.org/analysis/8/1r3k2/4ppp1/3q4/5PB1/4P3/4QK2/8_w_-_-_0_1
        ("8/1r3k2/4ppp1/3q4/5PB1/4P3/4QK2/8 w - - 0 1", "['g4f3']", True, True,),
        # https://lichess.org/analysis/2Q5/1p4q1/p2B1k2/6p1/P3b3/7P/5PP1/6K1_w_-_-_0_1
        (
            "2Q5/1p4q1/p2B1k2/6p1/P3b3/7P/5PP1/6K1 w - - 0 1",
            "['d6e5', 'f6e5', 'c8c3']",
            True,
            False,
        ),
        # It's almost a skewer but the attacked piece has lower value
        # https://lichess.org/analysis/5rk1/2r2pp1/7p/8/2b5/7P/5PP1/5RK1_w_-_-_0_1
        ("5rk1/2r2pp1/7p/8/2b5/7P/5PP1/5RK1 w - - 0 1", "['f1c1']", False, False,),
        # It's almost a skewer but the piece hidden behind the attacked piece can be defended by the attacked piece
        # https://lichess.org/analysis/5rk1/2b2pp1/7p/8/8/2q1B2P/5PP1/5RK1_w_-_-_0_1
        ("5rk1/2b2pp1/7p/8/8/2q1B2P/5PP1/5RK1 w - - 0 1", "['f1c1']", False, False,),
        # It's almost the skewer but the attacked piece can capture the attacking piece because it is undefended
        # https://lichess.org/analysis/3b1rk1/5p1p/6pq/4Q3/8/7P/5PP1/R5K1_b_-_-_0_1
        ("3b1rk1/5p1p/6pq/4Q3/8/7P/5PP1/R5K1 b - - 0 1", "['d8f6']", False, False,),
        # Not a skewer, rook gives a check but doesn't skewer anything behind the king
        # https://lichess.org/analysis/6k1/4Rpbp/p5p1/8/2pr4/7P/PP3PP1/3R2K1_w_-_-_0_1
        ("6k1/4Rpbp/p5p1/8/2pr4/7P/PP3PP1/3R2K1 w - - 0 1", "['e7e8']", False, False),
        # It is a skewer, rook attack kings and skewers the rook behind it, but the move
        # is also a checkmate
        # https://lichess.org/analysis/rn3k1r/ppp3pp/3N1p2/4R3/P1B5/5b2/1P3PPP/R1B3K1_w_-_-_0_1
        (
            "rn3k1r/ppp3pp/3N1p2/4R3/P1B5/5b2/1P3PPP/R1B3K1 w - - 0 1",
            "['e5e8']",
            True,
            True,
        ),
        # Not a skewer, rook attacks the king and nothing hides behind the king
        # https://lichess.org/analysis/5r1k/1bp1n2p/p5pB/4q3/1p1PP3/P7/1P2N1PP/3R1R1K_w_-_-_0_1
        (
            "5r1k/1bp1n2p/p5pB/4q3/1p1PP3/P7/1P2N1PP/3R1R1K w - - 0 1",
            "['f1f8']",
            False,
            False,
        ),
        # Not a skewer, queen just gives a check
        # https://lichess.org/analysis/2r2rk1/p2b2pp/3p4/q3p3/3Pp3/2N3P1/PP3P1P/R2Q1RK1_w_-_-_0_1
        (
            "2r2rk1/p2b2pp/3p4/q3p3/3Pp3/2N3P1/PP3P1P/R2Q1RK1 w - - 0 1",
            "['d1b3']",
            False,
            False,
        ),
        # Not a skewer, rook attacks a pawn and it's probably impossible to make a skewer attacking a pawn
        # https://lichess.org/analysis/2r2rk1/p2b2pp/3p4/q3p3/3Pp3/2N3P1/PP3P1P/R2Q1RK1_w_-_-_0_1
        (
            "2r2rk1/p2b2pp/3p4/q3p3/3Pp3/2N3P1/PP3P1P/R2Q1RK1 w - - 0 1",
            "['f1e1']",
            False,
            False,
        ),
        # It is a skewer, rook attacks a queen and when the queen moves, it uncovers attack on their rook
        # https://lichess.org/analysis/2r2r1k/p5pp/3p1q2/3Q4/4R3/2N3Pb/PP3P1P/R5K1_w_-_-_0_1
        (
            "2r2r1k/p5pp/3p1q2/3Q4/4R3/2N3Pb/PP3P1P/R5K1 w - - 0 1",
            "['e4f4']",
            True,
            True,
        ),
        # Definitely not a skewer, queen gives checkmate on f7 and nothing hides behind their king
        # https://lichess.org/analysis/r2q1rk1/5ppp/p1p3n1/1p1n2NQ/3Pb3/1BP5/PP4PP/R3R1K1_w_-_-_0_1
        (
            "r2q1rk1/5ppp/p1p3n1/1p1n2NQ/3Pb3/1BP5/PP4PP/R3R1K1 w - - 0 1",
            "['h5h7']",
            False,
            False,
        ),
        # Not a skewer, the move attacks a pawn and it's probably impossible to make a skewer attacking a pawn
        # https://lichess.org/analysis/6k1/pp3pb1/6p1/2p5/PnP5/R2P1KP1/1P3P2/2B1r3_w_-_-_0_1
        (
            "6k1/pp3pb1/6p1/2p5/PnP5/R2P1KP1/1P3P2/2B1r3 w - - 0 1",
            "['c1c3']",
            False,
            False,
        ),
        # Not a skewer, it's rather a discovered attack
        # https://lichess.org/analysis/r2q1rk1/4p1bp/2p3p1/pp2P2n/8/2NB3Q/PPP2PP1/2KR3R_w_-_-_0_1
        (
            "r2q1rk1/4p1bp/2p3p1/pp2P2n/8/2NB3Q/PPP2PP1/2KR3R w - - 0 1",
            "['d3g6']",
            False,
            False,
        ),
        # Not a skewer, the rook check the king and when the king cannot move to defend the rook hidden behind it, but
        # that rook is already defended by a bishop
        # https://lichess.org/analysis/4kr2/pp6/3b2bp/3Bn1p1/8/1P3NPP/PP5K/2R2R2_w_-_-_0_1
        (
            "4kr2/pp6/3b2bp/3Bn1p1/8/1P3NPP/PP5K/2R2R2 w - - 0 1",
            "['c1c8']",
            False,
            False,
        ),
    ],
)
def test_skewer(fen, pv, expected_contains_skewer, expected_is_first_move_skewer):
    f = features.Motives(fen, pv)
    assert f.features()["contains_skewer"] == expected_contains_skewer
    assert f.features()["is_first_move_skewer"] == expected_is_first_move_skewer


@pytest.mark.parametrize(
    "fen, pv, expected_contains_pin, expected_is_first_move_pin",
    [
        # Absolute pin
        # https://lichess.org/analysis/1rk5/1p6/4n3/8/4B3/8/3R3P/3K4_w_-_-_0_1
        ("1rk5/1p6/4n3/8/4B3/8/3R3P/3K4 w - - 0 1", "['e4f5']", True, True,),
        # Relative pin
        # https://lichess.org/analysis/1kr5/4p3/4n3/8/4B3/8/3R3P/3K4_w_-_-_0_1
        ("1kr5/4p3/4n3/8/4B3/8/3R3P/3K4 w - - 0 1", "['e4f5']", True, True,),
        # Relative pin in opening phase
        # https://lichess.org/analysis/r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R_b_KQkq_-_0_1
        (
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 1",
            "['d7d6', 'c2c3', 'c8g4']",
            True,
            False,
        ),
        # Pin called a partial pin because the pinned piece can still move along the line of the attack
        # https://lichess.org/analysis/4k3/1p6/8/4q3/8/8/1P6/3R1K2_w_-_-_0_1
        ("4k3/1p6/8/4q3/8/8/1P6/3R1K2 w - - 0 1", "['d1e1']", True, True,),
        # Not a pin because it is skewer
        # https://lichess.org/analysis/1kn5/4p3/4r3/8/4B3/8/3R3P/3K4_w_-_-_0_1
        ("1kn5/4p3/4r3/8/4B3/8/3R3P/3K4 w - - 0 1", "['e4f5']", False, False,),
        # Not a pin because the attacked piece can capture the attacker of the same value
        # https://lichess.org/analysis/1kq5/1pp5/p3b3/8/8/8/5NBP/5QK1_w_-_-_0_1
        ("1kq5/1pp5/p3b3/8/8/8/5NBP/5QK1 w - - 0 1", "['g2h3']", False, False,),
        # Not a pin because the attacked piece can capture the attacker of the greater value
        # https://lichess.org/analysis/1kq5/1pp5/p3b3/8/8/8/5NQP/5BK1_w_-_-_0_1
        ("1kq5/1pp5/p3b3/8/8/8/5NQP/5BK1 w - - 0 1", "['g2h3']", False, False,),
        # Not a pin because the attacked piece can capture undefended attacker of the lower value
        # https://lichess.org/analysis/2k5/1pp5/p3q3/8/8/8/6BP/6KQ_w_-_-_0_1
        ("2k5/1pp5/p3q3/8/8/8/6BP/6KQ w - - 0 1", "['g2h3']", False, False,),
        # Not a pin because it is skewer
        # https://lichess.org/analysis/r1bqkbnr/ppp2ppp/2np4/4p3/4P3/2P2N2/PP1PBPPP/RNBQK2R_b_KQkq_-_0_1
        (
            "r1bqkbnr/ppp2ppp/2np4/4p3/4P3/2P2N2/PP1PBPPP/RNBQK2R b KQkq - 0 1",
            "['c8g4']",
            False,
            False,
        ),
        #
    ],
)
def test_pin(fen, pv, expected_contains_pin, expected_is_first_move_pin):
    f = features.Motives(fen, pv)
    assert f.features()["contains_pin"] == expected_contains_pin
    assert f.features()["is_first_move_pin"] == expected_is_first_move_pin


@pytest.mark.parametrize(
    "fen, pv, expected_contains_sacrifice, expected_is_first_move_sacrifice",
    [
        # king's gambit
        # https://lichess.org/analysis/rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR_w_KQkq_-_0_1
        (
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1",
            "['f2f4']",
            True,
            True,
        ),
        # greek's gift
        # https://lichess.org/analysis/r1bq1rk1/pp2nppp/2n1p3/3pP3/3P4/2PB1N2/P4PPP/R1BQK2R_w_KQq_-_0_1
        (
            "r1bq1rk1/pp2nppp/2n1p3/3pP3/3P4/2PB1N2/P4PPP/R1BQK2R w KQq - 0 1",
            "['d3h7']",
            True,
            True,
        ),
        # similar to greek's gift but not a sacrifice since the captured piece has same value as the capturing piece
        # https://lichess.org/analysis/r1bq1rk1/pp3ppn/2n1p3/3pP3/3P4/2PB1N2/P4PPP/R1BQK2R_w_KQq_-_0_1
        (
            "r1bq1rk1/pp3ppn/2n1p3/3pP3/3P4/2PB1N2/P4PPP/R1BQK2R w KQq - 0 1",
            "['d3h7']",
            False,
            False,
        ),
        # not a sacrifice because we can recapture if opponent captures
        # https://lichess.org/analysis/2r3k1/2r2ppp/8/8/2B5/8/5PPP/2R2RK1_b_-_-_0_1
        ("2r3k1/2r2ppp/8/8/2B5/8/5PPP/2R2RK1 b - - 0 1", "['c7c4']", False, False,),
        # a sacrifice, we sacrifice a rook but if opponent accepts then we can check mate
        # https://lichess.org/analysis/2rr2k1/5ppp/8/8/2B5/5R2/5PPP/2R3K1_b_-_-_0_1
        ("2rr2k1/5ppp/8/8/2B5/5R2/5PPP/2R3K1 b - - 0 1", "['c8c4']", True, True,),
        # not a sacrifice because the piece we capture is not defended
        # https://lichess.org/analysis/2r1r1k1/5ppp/8/8/2B5/5R2/5PPP/3R2K1_b_-_-_0_1
        ("2r1r1k1/5ppp/8/8/2B5/5R2/5PPP/3R2K1 b - - 0 1", "['c8c4']", False, False,),
        # sacrifice, main queen's gambit line
        (chess.STARTING_FEN, "['d2d4', 'd7d5', 'c2c4', 'e7e6']", True, False,),
    ],
)
def test_sacrifice(
    fen, pv, expected_contains_sacrifice, expected_is_first_move_sacrifice
):
    f = features.Motives(fen, pv)
    assert f.features()["contains_sacrifice"] == expected_contains_sacrifice
    assert f.features()["is_first_move_sacrifice"] == expected_is_first_move_sacrifice


@pytest.mark.parametrize(
    "fen, pv, our_expected, their_expected",
    [
        # https://lichess.org/analysis/6kq/8/8/4n3/4p3/8/5P2/4RBK1_b_-_-_0_1
        (
            "6kq/8/8/4n3/4p3/8/5P2/4RBK1 b - - 0 1",
            "['e5f3', 'g1g2', 'h8h2']",
            [chess.KNIGHT, chess.QUEEN],
            [chess.KING],
        ),
        # https://lichess.org/analysis/8/8/8/8/1N3K1k/8/8/3Q4_w_-_-_0_1
        ("8/8/8/8/1N3K1k/8/8/3Q4 w - - 0 1", "['d1h1']", [chess.QUEEN], []),
        (
            chess.STARTING_FEN,
            "['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5', 'a7a6', 'b5c6', 'd7c6']",
            [chess.PAWN, chess.KNIGHT, chess.BISHOP,],
            [chess.PAWN, chess.KNIGHT,],
        ),
    ],
)
def test_best_pv_moved_piece_types(fen, pv, our_expected, their_expected):
    f = features.BestPV(fen, pv)
    assert f.features()["best_pv_our_moved_piece_types"] == our_expected
    assert f.features()["best_pv_their_moved_piece_types"] == their_expected


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
