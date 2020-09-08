import subprocess
from ast import literal_eval

import pytest
import chess
import chess.engine
import features
import pandas as pd
from board import Tactic, Threat, CheckmateType, PawnStructure
from features.helpers import square_from_name
from features.board import GamePhase, PositionOpenness


@pytest.mark.parametrize(
    "fen, expected",
    [
        ("8/pp3ppp/2p1p3/8/3P4/8/PPP2PPP/8 w - - 0 1", PawnStructure.CARO),
        ("8/pp3ppp/2p1p3/8/3P4/4P3/PP3PPP/8 w - - 0 1", PawnStructure.SLAV),
        (
            "8/pp3ppp/3pp3/8/4P3/8/PPP2PPP/8 w - - 0 1",
            PawnStructure.SICILIAN_SCHEVENINGEN,
        ),
        ("8/pp2pp1p/3p2p1/8/4P3/8/PPP2PPP/8 w - - 0 1", PawnStructure.SICILIAN_DRAGON),
        (
            "8/pp3ppp/3p4/4p3/4P3/8/PPP2PPP/8 w - - 0 1",
            PawnStructure.SICILIAN_BOLESLAVSKY_HOLE,
        ),
        ("8/pp1ppppp/8/8/2P1P3/8/PP3PPP/8 w - - 0 1", PawnStructure.MAROCZY_BIND),
        ("8/5ppp/pp1pp3/8/2P1P3/8/PP3PPP/8 w - - 0 1", PawnStructure.HEDGEHOG),
        ("8/pp3ppp/2p5/4p3/2P1P3/8/PP3PPP/8 w - - 0 1", PawnStructure.RAUZER_FORMATION),
        ("8/pp3ppp/2pp4/8/2P1P3/8/PP3PPP/8 w - - 0 1", PawnStructure.BOLESLAVSKY_WALL),
        ("8/ppp2ppp/3p4/3Pp3/4P3/8/PPP2PPP/8 w - - 0 1", PawnStructure.D5_CHAIN),
        ("8/ppp2ppp/4p3/3pP3/3P4/8/PPP2PPP/8 w - - 0 1", PawnStructure.E5_CHAIN),
        ("8/pp3ppp/3p4/2pP4/4P3/8/PP3PPP/8 w - - 0 1", PawnStructure.MODERN_BENONI),
        ("8/ppp2ppp/8/8/3P4/8/PP3PPP/8 w - - 0 1", PawnStructure.GIUOCO_PIANO_ISOLANI),
        (
            "8/pp3ppp/4p3/8/3P4/8/PP3PPP/8 w - - 0 1",
            PawnStructure.QUEENS_GAMBIT_ISOLANI,
        ),
        ("8/pp3ppp/4p3/8/2PP4/8/P4PPP/8 w - - 0 1", PawnStructure.HANGING_PAWNS),
        ("8/pp3ppp/2p5/3p4/3P4/4P3/PP3PPP/8 w - - 0 1", PawnStructure.CARLSBAD),
        ("8/pp3ppp/4p3/2Pp4/3P4/8/PP3PPP/8 w - - 0 1", PawnStructure.PANOV),
        ("8/ppp3pp/4p3/3p1p2/3P1P2/4P3/PPP3PP/8 w - - 0 1", PawnStructure.STONEWALL),
        (
            "8/pp3ppp/3p4/2p1p3/2P1P3/3P4/PP3PPP/8 w - - 0 1",
            PawnStructure.BOTVINNIK_SYSTEM,
        ),
        (
            "8/pp2pppp/3p4/2p5/4P3/3P4/PPP2PPP/8 w - - 0 1",
            PawnStructure.CLOSED_SICILIAN,
        ),
    ],
)
def test_pawn_structure(fen, expected):
    pawn_structures = features.Board(fen).pawn_structure
    assert pawn_structures == expected


@pytest.mark.parametrize(
    "fen, expected",
    [
        # https://lichess.org/analysis/rnbqnrk1/pp2bppp/3p4/2pPp3/2P1P3/2NBB3/PP2QPPP/R3K1NR_w_KQ_-_0_1
        (
            "rnbqnrk1/pp2bppp/3p4/2pPp3/2P1P3/2NBB3/PP2QPPP/R3K1NR w KQ - 0 1",
            {"c4", "c5", "d5", "d6", "e4", "e5"},
        ),
        # https://lichess.org/analysis/r5k1/pp2rppp/1n2bn2/2R5/3QPq2/P4PN1/1B2B1PP/5RK1_w_-_-_0_1
        ("r5k1/pp2rppp/1n2bn2/2R5/3QPq2/P4PN1/1B2B1PP/5RK1 w - - 0 1", set(),),
        # https://lichess.org/analysis/rn1qk2r/pb2bppp/1p1ppn2/8/2PQ4/2N2NP1/PP2PPBP/R1B2RK1_w_kq_-_0_1
        ("rn1qk2r/pb2bppp/1p1ppn2/8/2PQ4/2N2NP1/PP2PPBP/R1B2RK1 w kq - 0 1", set(),),
        # https://lichess.org/editor/rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR_w_KQkq_-_0_1
        ("rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 1", {"d4"},),
        # https://lichess.org/editor/rnbqkbnr/pp2pppp/2p5/2Pp4/3PP3/8/PP3PPP/RNBQKBNR_w_KQkq_-_0_1
        (
            "rnbqkbnr/pp2pppp/2p5/2Pp4/3PP3/8/PP3PPP/RNBQKBNR w KQkq - 0 1",
            {"c5", "c6", "d4"},
        ),
    ],
)
def test_locked_pawns(fen, expected):
    locked_pawns = features.Board._locked_pawns(fen)
    assert locked_pawns == {square_from_name(square_name) for square_name in expected}


@pytest.mark.parametrize(
    "fen, expected",
    [
        # source: https://www.chessstrategyonline.com/content/tutorials/basic-chess-concepts-phases-of-the-game
        (
            "r1bqkb1r/pp2pppp/2np1n2/6B1/3NP3/2N5/PPP2PPP/R2QKB1R w KQkq - 0 1",
            GamePhase.OPENING,
        ),
        (
            "r5k1/4bppp/p1q1p3/2p1P3/Pr4n1/1PNQB3/2P3PP/3R1RK1 w - - 0 1",
            GamePhase.MIDDLEGAME,
        ),
        ("8/5ppk/4p2p/4P3/8/1r6/p5P1/4R1K1 w - - 0 1", GamePhase.ENDGAME),
        # source: https://www.chess.com/forum/view/general/the-3-chess-phases
        (
            "r1bq1rk1/pppp1ppp/2n2n2/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQ1RK1 w - - 0 1",
            GamePhase.OPENING,
        ),
        (
            "1q3rk1/3n1rbp/1p1p2p1/p1pPp3/2P1PpP1/PPNB1P2/1KQ4P/3R3R w - - 0 1",
            GamePhase.MIDDLEGAME,
        ),
        (
            "1q3r1k/3n1rbp/1p1p2p1/p1pPp1PP/2P1PpB1/PPN2P2/1K5Q/6RR b - - 0 8",
            GamePhase.MIDDLEGAME,
        ),
        ("8/1p3pp1/p1krpn1p/P6P/2P2PP1/2B5/1PK5/4R3 w - - 0 1", GamePhase.ENDGAME),
        ("2Q5/8/p3p3/P4p1k/8/8/8/3K4 b - - 0 13", GamePhase.ENDGAME),
        # source: https://www.mark-weeks.com/aboutcom/ble24phs.htm
        (
            "r1bq1rk1/pp1nbppp/2p1pn2/3p2B1/2PP4/P1NBPN2/1P3PPP/R2QK2R w KQ - 0 1",
            GamePhase.OPENING,
        ),
        (
            "2r2r2/pp1bqpk1/1n3npp/4p3/4P3/P4NNP/BP1Q1PP1/2R2RK1 w - - 0 1",
            GamePhase.MIDDLEGAME,
        ),
        ("8/5p1k/5rpp/8/P2R3P/6P1/5PK1/8 w - - 0 1", GamePhase.ENDGAME),
        # source: https://thechessworld.com/articles/middle-game/7-most-important-middlegame-principles/
        (
            "r2q1rk1/1p1b1ppp/p1n1pn2/3p4/1P3B2/P1NQ1N1P/1P3PP1/3RR1K1 w - - 0 1",
            GamePhase.MIDDLEGAME,
        ),
        (
            "r4rk1/pb2ppbp/1p3np1/8/2P5/1PN1pN2/1B1PQPPP/3R1RK1 w - - 0 1",
            GamePhase.MIDDLEGAME,
        ),
        # TODO discuss how the one below should be classified
        ("1r2r1k1/p4ppp/b1p2n2/8/8/P1N2P2/1P3PBP/1K1RR3 w - - 0 1", GamePhase.ENDGAME),
        (
            "2kr2r1/1pp2p2/p1n4p/4n3/P5pP/N1P3P1/1PQ2PBK/3R1R2 w - - 0 1",
            GamePhase.MIDDLEGAME,
        ),
        (
            "1k1rr3/1pp1qpp1/p1n2nbp/8/PP2pP2/1NP1N1P1/2Q3BP/4RR1K w - - 0 1",
            GamePhase.MIDDLEGAME,
        ),
        (
            "r4rk1/pp2qpbp/4pnp1/3p4/3P4/P3PP2/1PR1NQPP/2R2BK1 w - - 0 1",
            GamePhase.MIDDLEGAME,
        ),
        (
            "2rr2k1/pq3ppp/1pp2nn1/8/1P2P3/PB3P2/1B4PP/1Q1R1RK1 w - - 0 1",
            GamePhase.MIDDLEGAME,
        ),
        # source: https://thechessworld.com/articles/endgame/5-most-effective-endgame-ideas-every-beginner-should-know/
        (
            "r1b1r3/pp3p2/2p2k1p/P3p1p1/6P1/1P2R2P/2P1PPB1/2KR4 w - - 0 1",
            GamePhase.ENDGAME,
        ),
        ("R7/5p2/P5pp/8/7P/6P1/r4PK1/8 w - - 0 1", GamePhase.ENDGAME),
        ("3rr1k1/ppp2pbp/6p1/8/6b1/1NP1B3/PP3PPP/R4RK1 w - - 0 1", GamePhase.ENDGAME),
    ],
)
def test_game_phase(fen, expected):
    phase = features.Board(fen).phase
    assert phase == expected


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
            ["f4c4", "g8h8", "g5f7", "h8g8", "f7h6", "g8h8", "c4g8", "e8g8", "h6f7"],
            True,
        ),
        # https://lichess.org/analysis/rnbq1r1k/ppp1npp1/4p3/b2pP1N1/3P4/2P5/PP3PPP/RNBQK2R_w_KQ_-_0_1
        (
            "rnbq1r1k/ppp1npp1/4p3/b2pP1N1/3P4/2P5/PP3PPP/RNBQK2R w KQ - 2 9",
            ["d1h5", "h8g8", "h5h7"],
            False,
        ),
        # https://lichess.org/analysis/r1bqkb1r/1p1nppp1/p2p1n1p/1N6/8/8/PPPPQPPP/R1B1KBNR_w_KQkq_-_0_1
        (
            "r1bqkb1r/1p1nppp1/p2p1n1p/1N6/8/8/PPPPQPPP/R1B1KBNR w KQkq - 0 1",
            ["b5d6"],
            True,
        ),
    ],
)
def test_smothered_mate(fen, pv, expected):
    f = features.CheckmateType(fen, pv)
    assert (CheckmateType.SMOTHERED in f._checkmate_types()) == expected


@pytest.mark.parametrize(
    "fen, pv, expected",
    [
        # https://lichess.org/analysis/6k1/5ppp/8/8/8/8/5PPP/3R2K1_w_-_-_0_1
        ("6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1", ["d1d8"], True,),
        # https://lichess.org/analysis/8/1p2Q3/8/8/k1K5/8/8/8_w_-_-_0_1
        ("8/1p2Q3/8/8/k1K5/8/8/8 w - - 0 1", ["e7b4"], False,),
        # https://lichess.org/analysis/3r2k1/5ppp/8/8/8/8/5PPP/6K1_b_-_-_0_1
        ("3r2k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1", ["d8d1"], True,),
        # https://lichess.org/analysis/8/1P2q3/8/8/K1k5/8/8/8_b_-_-_0_1
        ("8/1P2q3/8/8/K1k5/8/8/8 b - - 0 1", ["e7b4"], False,),
        # https://lichess.org/analysis/6k1/3P1ppp/8/8/8/8/5PPP/6K1_w_-_-_0_1
        ("6k1/3P1ppp/8/8/8/8/5PPP/6K1 w - - 0 1", ["d7d8q"], True),
    ],
)
def test_back_rank_mate(fen, pv, expected):
    f = features.CheckmateType(fen, pv)
    assert (CheckmateType.BACK_RANK in f._checkmate_types()) == expected


@pytest.mark.parametrize(
    "fen, pv, expected",
    [
        # https://lichess.org/analysis/8/8/8/7k/8/6q1/5r2/4K3_b_-_-_0_1
        ("8/8/8/7k/8/6q1/5r2/4K3 b - - 0 1", ["g3g1"], True)
    ],
)
def test_mate_with_queen_rook(fen, pv, expected):
    f = features.CheckmateType(fen, pv)
    assert (CheckmateType.QUEEN_ROOK in f._checkmate_types()) == expected


@pytest.mark.parametrize(
    "fen, pv, expected",
    [
        # https://lichess.org/analysis/8/8/8/7k/8/6r1/7r/4K3_b_-_-_0_1
        ("8/8/8/7k/8/6r1/7r/4K3 b - - 0 1", ["g3g1"], True)
    ],
)
def test_mate_with_rook_rook(fen, pv, expected):
    f = features.CheckmateType(fen, pv)
    assert (CheckmateType.ROOK_ROOK in f._checkmate_types()) == expected


@pytest.mark.parametrize(
    "fen, pv, expected",
    [
        # https://lichess.org/analysis/3Q4/8/8/7k/5K2/8/8/8_w_-_-_0_1
        ("3Q4/8/8/7k/5K2/8/8/8 w - - 0 1", ["d8g5"], True)
    ],
)
def test_mate_with_king_queen(fen, pv, expected):
    f = features.CheckmateType(fen, pv)
    assert (CheckmateType.KING_QUEEN in f._checkmate_types()) == expected


@pytest.mark.parametrize(
    "fen, pv, expected",
    [
        # https://lichess.org/analysis/8/5R2/8/5K1k/8/8/8/8_w_-_-_0_1
        ("8/5R2/8/5K1k/8/8/8/8 w - - 0 1", ["f7h7"], True)
    ],
)
def test_mate_with_king_rook(fen, pv, expected):
    f = features.CheckmateType(fen, pv)
    assert (CheckmateType.KING_ROOK in f._checkmate_types()) == expected


@pytest.mark.parametrize(
    "fen, pv, expected",
    [
        # https://lichess.org/analysis/7k/5K2/8/5BB1/8/8/8/8_w_-_-_0_1
        ("7k/5K2/8/5BB1/8/8/8/8 w - - 0 1", ["g5f6"], True)
    ],
)
def test_mate_with_king_bishop_bishop(fen, pv, expected):
    f = features.CheckmateType(fen, pv)
    assert (CheckmateType.KING_BISHOP_BISHOP in f._checkmate_types()) == expected


@pytest.mark.parametrize(
    "fen, pv, expected",
    [
        # https://lichess.org/analysis/6k1/4B3/6K1/5N2/8/8/8/8_w_-_-_0_1
        ("6k1/4B3/6K1/5N2/8/8/8/8 w - - 0 1", ["f5h6", "g8h8", "e7f6"], True)
    ],
)
def test_mate_with_king_bishop_knight(fen, pv, expected):
    f = features.CheckmateType(fen, pv)
    assert (CheckmateType.KING_BISHOP_KNIGHT in f._checkmate_types()) == expected


@pytest.mark.parametrize(
    "fen, pv, expected_contains_tactic, expected_is_first_move_tactic",
    [
        # First move is a simple knight fork
        # https://lichess.org/analysis/3k4/N3q3/8/8/8/8/8/3K4_w_-_-_0_1
        ("3k4/N3q3/8/8/8/8/8/3K4 w - - 0 1", ["a7c6", "d8e8", "c6e7"], True, True,),
        # First move is a double attack with queen on king and knight
        # https://lichess.org/analysis/rnbqkb1r/pp2pppp/3p4/3P4/4n3/8/PP3PPP/RNBQKBNR_w_KQkq_-_0_1
        (
            "rnbqkb1r/pp2pppp/3p4/3P4/4n3/8/PP3PPP/RNBQKBNR w KQkq - 0 1",
            ["d1a4", "b8d7", "a4e4"],
            True,
            True,
        ),
        # Our first move is not a fork, but our second move is knight fork, from FIDE WCC 2004
        # https://lichess.org/analysis/r5k1/1p1q1pbp/6p1/2Pp4/p3nQ2/P4P2/B2B2PP/2R4K_b_-_-_0_1
        (
            "r5k1/1p1q1pbp/6p1/2Pp4/p3nQ2/P4P2/B2B2PP/2R4K b - - 0 1",
            ["e4f2", "h1g1", "f2d3", "f4e3", "d3c1"],
            True,
            False,
        ),
        # Known opening fork after capture
        # https://lichess.org/analysis/r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R_b_KQkq_-_0_1
        (
            "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R b KQkq - 0 1",
            ["f6e4", "c3e4", "d7d5", "c4d3", "d5e4"],
            True,
            False,
        ),
        # Starting position with some example line
        # https://lichess.org/analysis/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR_w_KQkq_-_0_1
        (
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            ["d2d4", "d7d5", "c2c4", "e7e6", "b1c3"],
            False,
            False,
        ),
        # First move forks the pieces but the second move is mate instead of a capture of one of forked pieces
        # https://lichess.org/analysis/6kq/8/8/4n3/4p3/8/5P2/4RBK1_b_-_-_0_1
        (
            "6kq/8/8/4n3/4p3/8/5P2/4RBK1 b - - 0 1",
            ["e4f3", "g1g2", "h8h2"],
            False,
            False,
        ),
    ],
)
def test_fork(fen, pv, expected_contains_tactic, expected_is_first_move_tactic):
    assert (
        Tactic.FORK in features.BestMove(fen, pv[0])._best_move_tactics()
    ) == expected_is_first_move_tactic
    assert (
        Tactic.FORK in features.BestPV(fen, pv)._best_pv_tactics()
    ) == expected_contains_tactic


@pytest.mark.parametrize(
    "fen, pv, expected_contains_tactic, expected_is_first_move_tactic",
    [
        # Tricky discovered attack
        # https://lichess.org/analysis/4q3/8/8/4k3/4B3/4R1r1/1K4P1/8_w_-_-_0_1
        ("4q3/8/8/4k3/4B3/4R1r1/1K4P1/8 w - - 0 1", ["e4f3"], True, True),
        # Trap in french advanced variation, discovered attack on undefended piece of same value as piece attacking it
        # https://lichess.org/analysis/r1b1kbnr/pp3ppp/4p3/3pP3/3q4/3B4/PP3PPP/RNBQK2R_w_KQkq_-_0_1
        (
            "r1b1kbnr/pp3ppp/4p3/3pP3/3q4/3B4/PP3PPP/RNBQK2R w KQkq - 0 1",
            ["d3b5"],
            True,
            True,
        ),
        # https://lichess.org/analysis/3rr1k1/pp2bpp1/2p4p/3p2q1/8/P3PPB1/1PP1QP1P/1K1R2R1_w_-_-_0_1
        (
            "3rr1k1/pp2bpp1/2p4p/3p2q1/8/P3PPB1/1PP1QP1P/1K1R2R1 w - - 0 1",
            ["g3c7"],
            True,
            True,
        ),
        # https://lichess.org/analysis/r3r1k1/pp2bpp1/2p1pn1p/8/2Pq4/2NB4/PP1Q1PPP/R3R1K1_w_-_-_0_1
        (
            "r3r1k1/pp2bpp1/2p1pn1p/8/2Pq4/2NB4/PP1Q1PPP/R3R1K1 w - - 0 1",
            ["d3h7"],
            True,
            True,
        ),
        # https://lichess.org/analysis/1r1qrbk1/1b3pp1/p1n2n1p/2p1p3/P3P3/2P2N1P/2BBQPP1/R2R1NK1_w_-_-_0_1
        (
            "1r1qrbk1/1b3pp1/p1n2n1p/2p1p3/P3P3/2P2N1P/2BBQPP1/R2R1NK1 w - - 0 1",
            ["d2h6"],
            True,
            True,
        ),
        # Double check and mate
        # https://lichess.org/analysis/5rk1/1p1q1ppp/pb3n2/2r1p1B1/4P3/1Q1P1R2/PP2N1PP/R5K1_b_-_-_0_1
        (
            "5rk1/1p1q1ppp/pb3n2/2r1p1B1/4P3/1Q1P1R2/PP2N1PP/R5K1 b - - 0 1",
            ["c5c1"],
            True,
            True,
        ),
        # Windmill
        # https://lichess.org/analysis/r3rnk1/pb3pp1/3ppB1p/7q/1P1P4/4N1R1/P4PPP/4R1K1_w_-_-_0_1
        (
            "r3rnk1/pb3pp1/3ppB1p/7q/1P1P4/4N1R1/P4PPP/4R1K1 w - - 0 1",
            ["g3g7", "g8h8", "g7f7", "h8g8"],
            True,
            False,
        ),
        # Check discovering an attack on undefended bishop by a queen
        # https://lichess.org/analysis/r4r2/pbpp2bk/1p2p1p1/7p/4NB1P/qP1P1QP1/2P2P2/3RR1K1_w_-_-_0_1
        (
            "r4r2/pbpp2bk/1p2p1p1/7p/4NB1P/qP1P1QP1/2P2P2/3RR1K1 w - - 0 1",
            ["e4g5"],
            True,
            True,
        ),
        # Moving a pawn to attack a rook discovers a check by a our rook
        # https://lichess.org/analysis/6r1/5p2/r1p1p3/B3np2/RP5k/2R4P/5P2/5K2_w_-_-_0_1
        ("6r1/5p2/r1p1p3/B3np2/RP5k/2R4P/5P2/5K2 w - - 0 1", ["b4b5"], True, True,),
        # Almost like a trap in french advanced variation but discovered attack on a defended piece of the same value
        # as the attacking piece
        # https://lichess.org/analysis/r1b1kbnr/pp3ppp/4p3/2ppP3/3q4/3B4/PP3PPP/RNBQK2R_w_KQkq_-_0_1
        (
            "r1b1kbnr/pp3ppp/4p3/2ppP3/3q4/3B4/PP3PPP/RNBQK2R w KQkq - 0 1",
            ["d3b5"],
            False,
            False,
        ),
        # Moving the bishop makes results in a rook that was behind it to attack a defended pawn
        # https://lichess.org/analysis/q2rr1k1/pp2bpp1/2p4p/3p4/8/P3PPB1/1PP1QP1P/1K1R2R1_w_-_-_0_1
        (
            "q2rr1k1/pp2bpp1/2p4p/3p4/8/P3PPB1/1PP1QP1P/1K1R2R1 w - - 0 1",
            ["g3c7"],
            False,
            False,
        ),
        # Check discovering an attack on a defended bishop by a queen
        # https://lichess.org/analysis/1r3r2/pbpp2bk/1p2p1p1/7p/4NB1P/qP1P1QP1/2P2P2/3RR1K1_w_-_-_0_1
        (
            "1r3r2/pbpp2bk/1p2p1p1/7p/4NB1P/qP1P1QP1/2P2P2/3RR1K1 w - - 0 1",
            ["e4g5"],
            False,
            False,
        ),
        # Not a discovered attack because opponent can capture the uncovered attacking piece
        # https://lichess.org/analysis/6k1/5p1p/4p1p1/1p1p2P1/6P1/8/R2K2r1/8_w_-_-_0_1
        ("6k1/5p1p/4p1p1/1p1p2P1/6P1/8/R2K2r1/8 w - - 0 1", ["d2e3"], False, False,),
        # Not a discovered attack because moving the king doesn't uncover any new attacker
        # https://lichess.org/analysis/8/pp6/3kB3/5P2/7K/2P3p1/P4n2/5R2_w_-_-_0_1
        ("8/pp6/3kB3/5P2/7K/2P3p1/P4n2/5R2 w - - 0 1", ["h4g3"], False, False,),
        # Discovered attack - moving the pawn uncovers queen attacking opponent's king
        # https://lichess.org/analysis/7N/6p1/8/2k2PQ1/6P1/8/6KP/8_w_-_-_0_1
        ("7N/6p1/8/2k2PQ1/6P1/8/6KP/8 w - - 0 1", ["f5f6"], True, True,),
        # Discovered attack - moving the bishop uncovers rook attacking opponent's king
        # https://lichess.org/analysis/8/1kB4R/r7/8/2P5/7P/2K5/8_w_-_-_0_1
        ("8/1kB4R/r7/8/2P5/7P/2K5/8 w - - 0 1", ["c7e5"], True, True,),
        # Not a discovered attack because moving the rook doesn't uncover any new attacker
        # https://lichess.org/analysis/7k/1p4p1/4K3/6b1/8/2r2P2/1r4PP/8_b_-_-_0_1
        ("7k/1p4p1/4K3/6b1/8/2r2P2/1r4PP/8 b - - 0 1", ["b2b5"], False, False),
        # Not a discovered attack because moving the rook doesn't uncover any new attacker
        # https://lichess.org/analysis/7k/1p4p1/8/5Kb1/8/2r2P2/4r1PP/8_b_-_-_0_1
        ("7k/1p4p1/8/5Kb1/8/2r2P2/4r1PP/8 b - - 0 1", ["c3c5"], False, False,),
        # Discovered attack - moving the rook uncovers bishop attacking opponent's king
        # https://lichess.org/analysis/7k/1pb3p1/8/4r3/2r5/5P1P/6PK/8_b_-_-_0_1
        ("7k/1pb3p1/8/4r3/2r5/5P1P/6PK/8 b - - 0 1", ["e5e1"], True, True,),
        # Not a discovered attack because capturing the knight with check doesn't uncover any new attacker
        # https://lichess.org/analysis/8/8/8/6P1/p3kp2/P2R4/8/2r1N1K1_b_-_-_0_1
        ("8/8/8/6P1/p3kp2/P2R4/8/2r1N1K1 b - - 0 1", ["c1e1"], False, False,),
        # Discovered attack, bishop captures a pawn and discovers our rook attacking their queen
        # https://lichess.org/analysis/r2q1rk1/4p1bp/2p3p1/pp2P2n/8/2NB3Q/PPP2PP1/2KR3R_w_-_-_0_1
        (
            "r2q1rk1/4p1bp/2p3p1/pp2P2n/8/2NB3Q/PPP2PP1/2KR3R w - - 0 1",
            ["d3g6"],
            True,
            True,
        ),
        # Not a discovered attack, a simply rook move
        # https://lichess.org/analysis/4r1k1/Q5pp/8/2p1p1q1/P1Pn1p2/3PR3/1P3PPP/3R2K1_w_-_-_0_1
        (
            "4r1k1/Q5pp/8/2p1p1q1/P1Pn1p2/3PR3/1P3PPP/3R2K1 w - - 0 1",
            ["e3e4"],
            False,
            False,
        ),
        # Not a discovered attack, just moving the queen
        # https://lichess.org/analysis/2k2r1r/1pp2p2/n6p/4N3/P2pp2P/3P2Pq/2PQ1P2/1R3RK1_w_-_-_0_1
        (
            "2k2r1r/1pp2p2/n6p/4N3/P2pp2P/3P2Pq/2PQ1P2/1R3RK1 w - - 0 1",
            ["d2f4"],
            False,
            False,
        ),
        # A discovered attack, moving the pawn discovers queen attacking their pawn
        # https://lichess.org/analysis/2k2r1r/1pp2p2/n6p/4N3/P2pp2P/3P2Pq/2PQ1P2/1R3RK1_w_-_-_0_1
        (
            "2k2r1r/1pp2p2/n6p/4N3/P2pp2P/3P2Pq/2PQ1P2/1R3RK1 w - - 0 1",
            ["d3e4"],
            True,
            True,
        ),
        # A discovered attack, capturing the pawn discovers our rook attacking their pawn and at the same time removes
        # the only defender of tha attacked pawn
        # https://lichess.org/analysis/5rk1/6qp/3p1p2/p1pPpPp1/2N1P1P1/P2Q3P/1P5K/2R2R2_w_-_-_0_1
        (
            "5rk1/6qp/3p1p2/p1pPpPp1/2N1P1P1/P2Q3P/1P5K/2R2R2 w - - 0 1",
            ["c4d6"],
            True,
            True,
        ),
        # Not a discovered attack, capturing the pawn discovers our rook attacking their pawn, but the pawn is defended
        # https://lichess.org/analysis/5rk1/6qp/3p1p2/p1pPpPp1/2N1P1P1/P2Q3P/1P5K/2R2R2_w_-_-_0_1
        (
            "5rk1/6qp/3p1p2/p1pPpPp1/2N1P1P1/P2Q3P/1P5K/2R2R2 w - - 0 1",
            ["c4a5"],
            False,
            False,
        ),
        # Rather not a discovered attack, moving the knight makes the rook that was previously defending their knight to
        # stop defending it, so their knight is not defended and our kings attacks it.
        # https://lichess.org/analysis/2r5/pp3k1p/2p1Npp1/8/2n5/3B2P1/P2bRP1P/6K1_b_-_-_0_1
        (
            "2r5/pp3k1p/2p1Npp1/8/2n5/3B2P1/P2bRP1P/6K1 b - - 0 1",
            ["c4e5"],
            False,
            False,
        ),
        # Not a discovered attack, the move discovers our queen attacking their pawn but the move is also a checkmate
        # https://lichess.org/analysis/2kr4/ppp1R2Q/8/5p2/8/6PP/PP2nq2/7K_b_-_-_0_1
        ("2kr4/ppp1R2Q/8/5p2/8/6PP/PP2nq2/7K b - - 0 1", ["e2g3"], False, False,),
        # A discovered attack that is checkmate at the same time, any knight move discovers our queen checkmating their
        # king
        # https://lichess.org/analysis/1n1rkr2/ppbp1pbn/1q1p1p1p/1N6/3P4/4N3/1PP1QPPP/R1B1KB1R_w_KQ_-_0_1
        (
            "1n1rkr2/ppbp1pbn/1q1p1p1p/1N6/3P4/4N3/1PP1QPPP/R1B1KB1R w KQ - 0 1",
            ["e3d1"],
            True,
            True,
        ),
    ],
)
def test_discovered_attack(
    fen, pv, expected_contains_tactic, expected_is_first_move_tactic
):
    assert (
        Tactic.DISCOVERED_ATTACK in features.BestMove(fen, pv[0])._best_move_tactics()
    ) == expected_is_first_move_tactic
    assert (
        Tactic.DISCOVERED_ATTACK in features.BestPV(fen, pv)._best_pv_tactics()
    ) == expected_contains_tactic


@pytest.mark.parametrize(
    "fen, pv, expected_contains_tactic, expected_is_first_move_tactic",
    [
        # https://lichess.org/analysis/8/3qk3/4b3/8/4KR2/5Q2/8/8_b_-_-_0_1
        ("8/3qk3/4b3/8/4KR2/5Q2/8/8 b - - 0 1", ["e6d5"], True, True,),
        # https://lichess.org/analysis/8/1r3k2/4ppp1/3q4/5PB1/4P3/4QK2/8_w_-_-_0_1
        ("8/1r3k2/4ppp1/3q4/5PB1/4P3/4QK2/8 w - - 0 1", ["g4f3"], True, True,),
        # https://lichess.org/analysis/2Q5/1p4q1/p2B1k2/6p1/P3b3/7P/5PP1/6K1_w_-_-_0_1
        (
            "2Q5/1p4q1/p2B1k2/6p1/P3b3/7P/5PP1/6K1 w - - 0 1",
            ["d6e5", "f6e5", "c8c3"],
            True,
            False,
        ),
        # It's almost a skewer but the attacked piece has lower value
        # https://lichess.org/analysis/5rk1/2r2pp1/7p/8/2b5/7P/5PP1/5RK1_w_-_-_0_1
        ("5rk1/2r2pp1/7p/8/2b5/7P/5PP1/5RK1 w - - 0 1", ["f1c1"], False, False,),
        # Not a skewer because the piece hidden behind the attacked piece can be defended by the attacked piece
        # https://lichess.org/analysis/5rk1/2b2pp1/7p/8/8/2q1B2P/5PP1/5RK1_w_-_-_0_1
        ("5rk1/2b2pp1/7p/8/8/2q1B2P/5PP1/5RK1 w - - 0 1", ["f1c1"], False, False,),
        # It's almost the skewer but the attacked piece can capture the attacking piece because it is undefended
        # https://lichess.org/analysis/3b1rk1/5p1p/6pq/4Q3/8/7P/5PP1/R5K1_b_-_-_0_1
        ("3b1rk1/5p1p/6pq/4Q3/8/7P/5PP1/R5K1 b - - 0 1", ["d8f6"], False, False,),
        # Not a skewer, rook gives a check but doesn't skewer anything behind the king
        # https://lichess.org/analysis/6k1/4Rpbp/p5p1/8/2pr4/7P/PP3PP1/3R2K1_w_-_-_0_1
        ("6k1/4Rpbp/p5p1/8/2pr4/7P/PP3PP1/3R2K1 w - - 0 1", ["e7e8"], False, False),
        # Not a skewer because the move is checkmate
        # https://lichess.org/analysis/rn3k1r/ppp3pp/3N1p2/4R3/P1B5/5b2/1P3PPP/R1B3K1_w_-_-_0_1
        (
            "rn3k1r/ppp3pp/3N1p2/4R3/P1B5/5b2/1P3PPP/R1B3K1 w - - 0 1",
            ["e5e8"],
            False,
            False,
        ),
        # Not a skewer, rook attacks the king and nothing hides behind the king
        # https://lichess.org/analysis/5r1k/1bp1n2p/p5pB/4q3/1p1PP3/P7/1P2N1PP/3R1R1K_w_-_-_0_1
        (
            "5r1k/1bp1n2p/p5pB/4q3/1p1PP3/P7/1P2N1PP/3R1R1K w - - 0 1",
            ["f1f8"],
            False,
            False,
        ),
        # Not a skewer, queen just gives a check
        # https://lichess.org/analysis/2r2rk1/p2b2pp/3p4/q3p3/3Pp3/2N3P1/PP3P1P/R2Q1RK1_w_-_-_0_1
        (
            "2r2rk1/p2b2pp/3p4/q3p3/3Pp3/2N3P1/PP3P1P/R2Q1RK1 w - - 0 1",
            ["d1b3"],
            False,
            False,
        ),
        # Not a skewer, rook attacks a pawn and it's probably impossible to make a skewer attacking a pawn
        # https://lichess.org/analysis/2r2rk1/p2b2pp/3p4/q3p3/3Pp3/2N3P1/PP3P1P/R2Q1RK1_w_-_-_0_1
        (
            "2r2rk1/p2b2pp/3p4/q3p3/3Pp3/2N3P1/PP3P1P/R2Q1RK1 w - - 0 1",
            ["f1e1"],
            False,
            False,
        ),
        # Not a skewer, rook attacks a queen and there is a rook hidden behind the queen but the queen has a move
        # to defend the hidden rook.
        # https://lichess.org/analysis/5r1k/p1r3pp/3p1q2/3Q4/4R3/2N3Pb/PP3P1P/R5K1_w_-_-_0_1
        (
            "5r1k/p1r3pp/3p1q2/3Q4/4R3/2N3Pb/PP3P1P/R5K1 w - - 0 1",
            ["e4f4"],
            False,
            False,
        ),
        # It is almost a skewer, rook attacks a queen and when the queen moves, it uncovers attack on their rook,
        # but that rook is defended so it would likely result in exchange of rooks
        # https://lichess.org/analysis/2r2r1k/p5pp/3p1q2/3Q4/4R3/2N3Pb/PP3P1P/R5K1_w_-_-_0_1
        (
            "2r2r1k/p5pp/3p1q2/3Q4/4R3/2N3Pb/PP3P1P/R5K1 w - - 0 1",
            ["e4f4"],
            False,
            False,
        ),
        # Definitely not a skewer, queen gives checkmate on f7 and nothing hides behind their king
        # https://lichess.org/analysis/r2q1rk1/5ppp/p1p3n1/1p1n2NQ/3Pb3/1BP5/PP4PP/R3R1K1_w_-_-_0_1
        (
            "r2q1rk1/5ppp/p1p3n1/1p1n2NQ/3Pb3/1BP5/PP4PP/R3R1K1 w - - 0 1",
            ["h5h7"],
            False,
            False,
        ),
        # Not a skewer, the move attacks a pawn and it's probably impossible to make a skewer attacking a pawn
        # https://lichess.org/analysis/6k1/pp3pb1/6p1/2p5/PnP5/R2P1KP1/1P3P2/2B1r3_w_-_-_0_1
        (
            "6k1/pp3pb1/6p1/2p5/PnP5/R2P1KP1/1P3P2/2B1r3 w - - 0 1",
            ["c1c3"],
            False,
            False,
        ),
        # Not a skewer, it's rather a discovered attack
        # https://lichess.org/analysis/r2q1rk1/4p1bp/2p3p1/pp2P2n/8/2NB3Q/PPP2PP1/2KR3R_w_-_-_0_1
        (
            "r2q1rk1/4p1bp/2p3p1/pp2P2n/8/2NB3Q/PPP2PP1/2KR3R w - - 0 1",
            ["d3g6"],
            False,
            False,
        ),
        # Not a skewer, the rook check the king and when the king cannot move to defend the rook hidden behind it, but
        # that rook is already defended by a bishop
        # https://lichess.org/analysis/4kr2/pp6/3b2bp/3Bn1p1/8/1P3NPP/PP5K/2R2R2_w_-_-_0_1
        (
            "4kr2/pp6/3b2bp/3Bn1p1/8/1P3NPP/PP5K/2R2R2 w - - 0 1",
            ["c1c8"],
            False,
            False,
        ),
        # The move is not a skewer, but a skewer already existed on the board
        # https://lichess.org/analysis/r4rk1/4bppp/2q5/8/8/5B2/5PPP/3RQRK1_w_-_-_0_1
        ("r4rk1/4bppp/2q5/8/8/5B2/5PPP/3RQRK1 w - - 0 1", ["d1c1"], False, False,),
        # Not a skewer, just bishop check
        # https://lichess.org/analysis/rnbqkbnr/ppp2ppp/8/3p4/2PP4/8/PP3PPP/RNBQKBNR_b_KQkq_-_0_1
        (
            "rnbqkbnr/ppp2ppp/8/3p4/2PP4/8/PP3PPP/RNBQKBNR b KQkq - 0 1",
            ["f8b4"],
            False,
            False,
        ),
        # Not a skewer because it is a pin
        # https://lichess.org/analysis/r3nrk1/7p/1pn2pp1/2pqp3/8/P1QBP3/1B3PPP/R4RK1_w_-_-_0_1
        (
            "r3nrk1/7p/1pn2pp1/2pqp3/8/P1QBP3/1B3PPP/R4RK1 w - - 0 1",
            ["d3c4"],
            False,
            False,
        ),
        # Not a skewer becaues it is a pin and discovered attack at the same time
        # https://lichess.org/analysis/rnb1k2r/ppp1qpbp/5np1/3p4/3P4/5N2/PPP1BPPP/RNBQR1K1_w_kq_-_0_1
        (
            "rnb1k2r/ppp1qpbp/5np1/3p4/3P4/5N2/PPP1BPPP/RNBQR1K1 w kq - 0 1",
            ["e2b5"],
            False,
            False,
        ),
        # Not a skewer, it is rather a pin
        (
            "1B1k2nb/pp2p2p/4bnp1/2p5/2P3P1/7P/PP3P2/R3KB1R w KQ - 0 1",
            ["b8e5"],
            False,
            False,
        ),
    ],
)
def test_skewer(fen, pv, expected_contains_tactic, expected_is_first_move_tactic):
    assert (
        Tactic.SKEWER in features.BestMove(fen, pv[0])._best_move_tactics()
    ) == expected_is_first_move_tactic
    assert (
        Tactic.SKEWER in features.BestPV(fen, pv)._best_pv_tactics()
    ) == expected_contains_tactic


@pytest.mark.parametrize(
    "fen, pv, expected_contains_tactic, expected_is_first_move_tactic",
    [
        # Absolute pin
        # https://lichess.org/analysis/1rk5/1p6/4n3/8/4B3/8/3R3P/3K4_w_-_-_0_1
        ("1rk5/1p6/4n3/8/4B3/8/3R3P/3K4 w - - 0 1", ["e4f5"], True, True,),
        # Relative pin
        # https://lichess.org/analysis/1kr5/4p3/4n3/8/4B3/8/3R3P/3K4_w_-_-_0_1
        ("1kr5/4p3/4n3/8/4B3/8/3R3P/3K4 w - - 0 1", ["e4f5"], True, True,),
        # Relative pin in opening phase
        # https://lichess.org/analysis/r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R_b_KQkq_-_0_1
        (
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 1",
            ["d7d6", "c2c3", "c8g4"],
            True,
            False,
        ),
        # Pin called a partial pin because the pinned piece can still move along the line of the attack
        # https://lichess.org/analysis/4k3/1p6/8/4q3/8/8/1P6/3R1K2_w_-_-_0_1
        ("4k3/1p6/8/4q3/8/8/1P6/3R1K2 w - - 0 1", ["d1e1"], True, True,),
        # Not a pin because it is skewer
        # https://lichess.org/analysis/1kn5/4p3/4r3/8/4B3/8/3R3P/3K4_w_-_-_0_1
        ("1kn5/4p3/4r3/8/4B3/8/3R3P/3K4 w - - 0 1", ["e4f5"], False, False,),
        # Not a pin because the attacked piece can capture the attacker of the same value
        # https://lichess.org/analysis/1kq5/1pp5/p3b3/8/8/8/5NBP/5QK1_w_-_-_0_1
        ("1kq5/1pp5/p3b3/8/8/8/5NBP/5QK1 w - - 0 1", ["g2h3"], False, False,),
        # Not a pin because the attacked piece can capture the attacker of the greater value
        # https://lichess.org/analysis/1kq5/1pp5/p3b3/8/8/8/5NQP/5BK1_w_-_-_0_1
        ("1kq5/1pp5/p3b3/8/8/8/5NQP/5BK1 w - - 0 1", ["g2h3"], False, False,),
        # Not a pin because the attacked piece can capture undefended attacker of the lower value
        # https://lichess.org/analysis/2k5/1pp5/p3q3/8/8/8/6BP/6KQ_w_-_-_0_1
        ("2k5/1pp5/p3q3/8/8/8/6BP/6KQ w - - 0 1", ["g2h3"], False, False,),
        # Not a pin because it is skewer
        # https://lichess.org/analysis/r1bqkbnr/ppp2ppp/2np4/4p3/4P3/2P2N2/PP1PBPPP/RNBQK2R_b_KQkq_-_0_1
        (
            "r1bqkbnr/ppp2ppp/2np4/4p3/4P3/2P2N2/PP1PBPPP/RNBQK2R b KQkq - 0 1",
            ["c8g4"],
            False,
            False,
        ),
        #
    ],
)
def test_pin(fen, pv, expected_contains_tactic, expected_is_first_move_tactic):
    assert (
        Tactic.PIN in features.BestMove(fen, pv[0])._best_move_tactics()
    ) == expected_is_first_move_tactic
    assert (
        Tactic.PIN in features.BestPV(fen, pv)._best_pv_tactics()
    ) == expected_contains_tactic


@pytest.mark.parametrize(
    "fen, pv, expected_contains_tactic, expected_is_first_move_tactic",
    [
        # king's gambit
        # https://lichess.org/analysis/rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR_w_KQkq_-_0_1
        (
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1",
            ["f2f4"],
            True,
            True,
        ),
        # greek's gift
        # https://lichess.org/analysis/r1bq1rk1/pp2nppp/2n1p3/3pP3/3P4/2PB1N2/P4PPP/R1BQK2R_w_KQq_-_0_1
        (
            "r1bq1rk1/pp2nppp/2n1p3/3pP3/3P4/2PB1N2/P4PPP/R1BQK2R w KQq - 0 1",
            ["d3h7"],
            True,
            True,
        ),
        # similar to greek's gift but not a sacrifice since the captured piece has same value as the capturing piece
        # https://lichess.org/analysis/r1bq1rk1/pp3ppn/2n1p3/3pP3/3P4/2PB1N2/P4PPP/R1BQK2R_w_KQq_-_0_1
        (
            "r1bq1rk1/pp3ppn/2n1p3/3pP3/3P4/2PB1N2/P4PPP/R1BQK2R w KQq - 0 1",
            ["d3h7"],
            False,
            False,
        ),
        # not a sacrifice because we can recapture if opponent captures
        # https://lichess.org/analysis/2r3k1/2r2ppp/8/8/2B5/8/5PPP/2R2RK1_b_-_-_0_1
        ("2r3k1/2r2ppp/8/8/2B5/8/5PPP/2R2RK1 b - - 0 1", ["c7c4"], False, False,),
        # a sacrifice, we sacrifice a rook but if opponent accepts then we can check mate
        # https://lichess.org/analysis/2rr2k1/5ppp/8/8/2B5/5R2/5PPP/2R3K1_b_-_-_0_1
        ("2rr2k1/5ppp/8/8/2B5/5R2/5PPP/2R3K1 b - - 0 1", ["c8c4"], True, True,),
        # not a sacrifice because the piece we capture is not defended
        # https://lichess.org/analysis/2r1r1k1/5ppp/8/8/2B5/5R2/5PPP/3R2K1_b_-_-_0_1
        ("2r1r1k1/5ppp/8/8/2B5/5R2/5PPP/3R2K1 b - - 0 1", ["c8c4"], False, False,),
        # sacrifice, main queen's gambit line
        (chess.STARTING_FEN, ["d2d4", "d7d5", "c2c4", "e7e6"], True, False,),
    ],
)
def test_sacrifice(fen, pv, expected_contains_tactic, expected_is_first_move_tactic):
    assert (
        Tactic.SACRIFICE in features.BestMove(fen, pv[0])._best_move_tactics()
    ) == expected_is_first_move_tactic
    assert (
        Tactic.SACRIFICE in features.BestPV(fen, pv)._best_pv_tactics()
    ) == expected_contains_tactic


@pytest.mark.parametrize(
    "fen, move, expected",
    [
        # https://lichess.org/analysis/rnbqkbnr/ppp2ppp/3p4/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR_w_KQkq_-_0_1
        (
            "rnbqkbnr/ppp2ppp/3p4/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 0 1",
            "d1h5",
            True,
        ),
        # https://lichess.org/analysis/r2qknnr/pppbbppp/3p4/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R_w_KQkq_-_0_1
        (
            "r2qknnr/pppbbppp/3p4/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1",
            "f3g5",
            True,
        ),
        # https://lichess.org/analysis/rnbqkbnr/ppp2ppp/3p4/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR_w_KQkq_-_0_1
        (
            "rnbqkbnr/ppp2ppp/3p4/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 0 1",
            "d1e2",
            False,
        ),
    ],
)
def test_mate_threat(fen, move, expected):
    assert (
        Threat.MATE in features.BestMove(fen, move)._best_move_threats()
    ) == expected


@pytest.mark.parametrize(
    "fen, move, expected",
    [
        # https://lichess.org/analysis/rnbqkb1r/ppp2ppp/3p4/4p3/4n3/5N2/PPPP1PPP/RNBQKB1R_w_KQkq_-_0_1
        (
            "rnbqkb1r/ppp2ppp/3p4/4p3/4n3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
            "c2c3",
            True,
        ),
        # https://lichess.org/analysis/rnb1kb1r/ppp2ppp/3p1n2/4pq2/8/2N5/PPPP1PPP/RNBQKB1R_w_KQkq_-_0_1
        (
            "rnb1kb1r/ppp2ppp/3p1n2/4pq2/8/2N5/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
            "c3b5",
            True,
        ),
        # https://lichess.org/analysis/r2qknnr/pppbbppp/3p4/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R_w_KQkq_-_0_1
        (
            "r2qknnr/pppbbppp/3p4/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1",
            "f3g5",
            True,
        ),
        # https://lichess.org/analysis/rnbqkbnr/ppp2ppp/3p4/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR_w_KQkq_-_0_1
        (
            "rnbqkbnr/ppp2ppp/3p4/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 0 1",
            "d1h5",
            False,
        ),
        # https://lichess.org/analysis/rnbqkbnr/ppp2ppp/3p4/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR_w_KQkq_-_0_1
        (
            "rnbqkbnr/ppp2ppp/3p4/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 0 1",
            "d1e2",
            False,
        ),
    ],
)
def test_fork_threat(fen, move, expected):
    assert (
        Threat.FORK in features.BestMove(fen, move)._best_move_threats()
    ) == expected


@pytest.mark.parametrize(
    "fen, move, expected",
    [
        # https://lichess.org/editor/rnb1kbnr/ppp1pppp/8/3q4/8/8/PPPP1PPP/RNBQKBNR_w_KQkq_-_0_1
        ("rnb1kbnr/ppp1pppp/8/3q4/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1", "b1c3", True),
        # https://lichess.org/editor/rnb1kbnr/ppp2ppp/4p3/3q4/8/8/PPPP1PPP/RNBQKBNR_w_KQkq_-_0_1
        ("rnb1kbnr/ppp2ppp/4p3/3q4/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1", "b1c3", False),
        # https://lichess.org/editor/rnb1kbnr/ppp1pppp/8/3q4/8/8/PPPP1PPP/RNBQKBNR_w_KQkq_-_0_1
        ("rnb1kbnr/ppp1pppp/8/3q4/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1", "b1a3", False),
    ],
)
def test_hanging_piece_capture_threat(fen, move, expected):
    assert (
        Threat.HANGING_PIECE_CAPTURE
        in features.BestMove(fen, move)._best_move_threats()
    ) == expected


@pytest.mark.parametrize(
    "fen, move, expected",
    [
        # https://lichess.org/editor/rnb1kbnr/ppp1pppp/8/3q4/8/8/PPPP1PPP/RNBQKBNR_w_KQkq_-_0_1
        ("rnb1kbnr/ppp1pppp/8/3q4/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1", "b1c3", True),
        # https://lichess.org/editor/rnb1kbnr/ppp2ppp/4p3/3q4/8/8/PPPP1PPP/RNBQKBNR_w_KQkq_-_0_1
        ("rnb1kbnr/ppp2ppp/4p3/3q4/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1", "b1c3", True),
        # https://lichess.org/editor/rn1qkbnr/ppp1pppp/8/3b3Q/8/8/PPPP1PPP/RNB1KBNR_w_KQkq_-_0_1
        ("rn1qkbnr/ppp1pppp/8/3b3Q/8/8/PPPP1PPP/RNB1KBNR w KQkq - 0 1", "b1c3", True),
        # https://lichess.org/editor/rn1qkbnr/ppp2ppp/4p3/3b4/8/8/PPPP1PPP/RNBQKBNR_w_KQkq_-_0_1
        ("rn1qkbnr/ppp2ppp/4p3/3b4/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1", "b1c3", False),
    ],
)
def test_material_gain_capture_threat(fen, move, expected):
    assert (
        Threat.MATERIAL_GAIN_CAPTURE
        in features.BestMove(fen, move)._best_move_threats()
    ) == expected


@pytest.mark.parametrize(
    "fen, pv, our_expected, their_expected",
    [
        # https://lichess.org/analysis/6kq/8/8/4n3/4p3/8/5P2/4RBK1_b_-_-_0_1
        (
            "6kq/8/8/4n3/4p3/8/5P2/4RBK1 b - - 0 1",
            ["e5f3", "g1g2", "h8h2"],
            [chess.KNIGHT, chess.QUEEN],
            [chess.KING],
        ),
        # https://lichess.org/analysis/8/8/8/8/1N3K1k/8/8/3Q4_w_-_-_0_1
        ("8/8/8/8/1N3K1k/8/8/3Q4 w - - 0 1", ["d1h1"], [chess.QUEEN], []),
        (
            chess.STARTING_FEN,
            ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6", "b5c6", "d7c6"],
            [chess.PAWN, chess.KNIGHT, chess.BISHOP],
            [chess.PAWN, chess.KNIGHT],
        ),
    ],
)
def test_best_pv_moved_piece_types(fen, pv, our_expected, their_expected):
    f = features.BestPV(fen, pv)
    assert f.features()["best_pv_our_moved_piece_types"] == our_expected
    assert f.features()["best_pv_their_moved_piece_types"] == their_expected


# TODO: test abstract.
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


def test_features_list():
    df = pd.DataFrame(
        [
            {
                "fen": chess.STARTING_FEN,
                "best_move": "e2e4",
                "best_pv": "['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5', 'a7a6', 'b5c6', 'd7c6']",
            }
        ]
    )
    df = features.FeatureList(
        [features.Board, features.BestMove, features.BestPV]
    ).from_df(df)
    assert len(df.columns) == 78
