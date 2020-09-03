import chess
import features


def test_best_pv_features():
    f = features.BestPV(
        chess.STARTING_FEN,
        ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6", "b5c6", "d7c6"],
    )
    # TODO: think about whether we want to expose lists and how to store.
    assert f.features() == {
        "best_pv_move_distance": 15,
        "best_pv_our_moved_piece_types": [1, 2, 3],
        "best_pv_our_number_of_captures": 1,
        "best_pv_our_number_of_checks": 0,
        "best_pv_our_number_of_pieces_moved": 3,
        "best_pv_tactic": 0,
        "best_pv_their_moved_piece_types": [1, 2],
        "best_pv_their_number_of_captures": 1,
        "best_pv_their_number_of_checks": 0,
        "best_pv_their_number_of_pieces_moved": 4,
        "best_pv_threat": 2,
        "best_pv_our_number_of_captures_normalized": 0.125,
        "best_pv_their_number_of_captures_normalized": 0.125,
        "best_pv_our_number_of_checks_normalized": 0.0,
        "best_pv_their_number_of_checks_normalized": 0.0,
        "best_pv_our_number_of_pieces_moved_normalized": 0.375,
        "best_pv_their_number_of_pieces_moved_normalized": 0.5,
    }
