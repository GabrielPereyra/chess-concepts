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
