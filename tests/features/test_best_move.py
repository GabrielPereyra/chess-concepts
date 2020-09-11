import pytest
import chess
import features


def test_best_move_features():
    f = features.BestMove(chess.STARTING_FEN, "e2e4")
    assert f.features() == {
        "best_move_captures_hanging_piece": False,
        "best_move_captures_piece_type": 0,
        "best_move_from_square": 12,
        "best_move_gives_check": False,
        "best_move_is_attacked": False,
        "best_move_is_backward": False,
        "best_move_is_capture": False,
        "best_move_is_capture_higher_value": False,
        "best_move_is_defended": False,
        "best_move_is_en_passant": False,
        "best_move_is_castling": False,
        "best_move_is_underpromotion": False,
        "best_move_is_forward": True,
        "best_move_is_horizontal": False,
        "best_move_is_promotion": False,
        "best_move_number_of_higher_value_pieces_attacked": 0,
        "best_move_number_of_pieces_attacked": 0,
        "best_move_piece_type": 1,
        "best_move_tactic": 0,
        "best_move_threat": 0,
        "best_move_to_square": 28,
        "best_move_was_attacked": False,
        "best_move_was_defended": True,
        "best_move_was_hanging": False,
    }


@pytest.mark.parametrize(
    "fen, move, expected",
    [
        # https://lichess.org/analysis/rnbqkbnr/ppp2ppp/3pp3/8/2BPP3/2N1BN2/PPPQ1PPP/R3K2R_w_KQkq_-_0_1
        (
            "rnbqkbnr/ppp2ppp/3pp3/8/2BPP3/2N1BN2/PPPQ1PPP/R3K2R w KQkq - 0 1",
            "e1g1",
            True,
        ),
        (
            "rnbqkbnr/ppp2ppp/3pp3/8/2BPP3/2N1BN2/PPPQ1PPP/R3K2R w KQkq - 0 1",
            "e1c1",
            True,
        ),
        (
            "rnbqkbnr/ppp2ppp/3pp3/8/2BPP3/2N1BN2/PPPQ1PPP/R3K2R w KQkq - 0 1",
            "e1f1",
            False,
        ),
        (
            "rnbqkbnr/ppp2ppp/3pp3/8/2BPP3/2N1BN2/PPPQ1PPP/R3K2R w KQkq - 0 1",
            "e1d1",
            False,
        ),
    ],
)
def test_best_move_is_castling(fen, move, expected):
    assert features.BestMove(fen, move).is_castling == expected


@pytest.mark.parametrize(
    "fen, move, expected",
    [
        # https://lichess.org/editor/rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPPP1PP/RNBQKBNR_w_KQkq_-_0_1
        ("rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPPP1PP/RNBQKBNR w KQkq e6 0 1", "f5e6", True),
        ("rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPPP1PP/RNBQKBNR w KQkq - 0 1", "f5e6", False),
        ("rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPPP1PP/RNBQKBNR w KQkq - 0 1", "f5f6", False),
    ],
)
def test_best_move_is_en_passant(fen, move, expected):
    assert features.BestMove(fen, move).is_en_passant == expected


@pytest.mark.parametrize(
    "fen, move, expected",
    [
        # https://lichess.org/analysis/5bnq/4Prkn/5ppp/8/8/8/5PPP/5RK1_w_-_-_0_1
        ("5bnq/4Prkn/5ppp/8/8/8/5PPP/5RK1 w - - 0 1", "e7e8k", True),
        ("5bnq/4Prkn/5ppp/8/8/8/5PPP/5RK1 w - - 0 1", "e7e8b", True),
        ("5bnq/4Prkn/5ppp/8/8/8/5PPP/5RK1 w - - 0 1", "e7e8r", True),
        ("5bnq/4Prkn/5ppp/8/8/8/5PPP/5RK1 w - - 0 1", "e7e8q", False),
        ("5bnq/4Prkn/5ppp/8/8/8/5PPP/5RK1 w - - 0 1", "f1e1", False),
    ],
)
def test_best_move_is_underpromotion(fen, move, expected):
    assert features.BestMove(fen, move).is_underpromotion == expected
