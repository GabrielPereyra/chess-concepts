import chess
import features
import pandas as pd


def test_board_features():
    f = features.Board(chess.STARTING_FEN)
    assert f.features() == {'fullmove_number': 1, 'is_check': False, 'our_number_of_bishop_moves': 0, 'our_number_of_captures': 0, 'our_number_of_checks': 0, 'our_number_of_knight_moves': 4, 'our_number_of_moves': 20, 'our_number_of_pawn_moves': 16, 'our_number_of_queen_moves': 0, 'our_number_of_rook_moves': 0, 'their_number_of_bishop_moves': 0, 'their_number_of_captures': 0, 'their_number_of_checks': 0, 'their_number_of_knight_moves': 4, 'their_number_of_moves': 20, 'their_number_of_pawn_moves': 16, 'their_number_of_queen_moves': 0, 'their_number_of_rook_moves': 0, 'turn': True}


def test_piece_count_features():
    f = features.PieceCount(chess.STARTING_FEN)
    assert f.features() == {'material_advantage': 0, 'our_bishops': 2, 'our_knights': 2, 'our_pawns': 8, 'our_piece_count': 16, 'our_queens': 1, 'our_rooks': 2, 'piece_count': 32, 'their_bishops': 2, 'their_knights': 2, 'their_pawns': 8, 'their_piece_count': 16, 'their_queens': 1, 'their_rooks': 2}


def test_best_move_features():
    f = features.BestMove(chess.STARTING_FEN, 'e2e4')
    assert f.features() == {'best_move_is_attacked': False, 'best_move_is_capture': False, 'best_move_is_check': False, 'best_move_is_defended': False, 'best_move_is_en_passant': False, 'best_move_is_promotion': False, 'best_move_piece_type': 1}


def test_best_pv_features():
    f = features.BestPV(chess.STARTING_FEN, "['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5', 'a7a6', 'b5c6', 'd7c6']")
    assert f.features() == {'best_pv_our_number_of_captures': 1, 'best_pv_our_number_of_checks': 0, 'best_pv_our_number_of_pieces_moved': 3, 'best_pv_their_number_of_captures': 1, 'best_pv_their_number_of_checks': 0, 'best_pv_their_number_of_pieces_moved': 4}


def test_smothered_mate_with_positive_example():
    # from a famous game:
    # https://www.chessgames.com/perl/chessgame?gid=1124489
    fen = '4r1k1/2pRP1pp/2p5/p4pN1/5Qn1/q5P1/P3PP1P/6K1 w - - 0 1'
    pv = "['f4c4', 'g8h8', 'g5f7', 'h8g8', 'f7h6', 'g8h8', 'c4g8', 'e8g8', 'h6f7']"

    f = features.Checkmate(fen, pv)
    assert f.features()['is_smothered_mate'] == 1


def test_smothered_mate_with_negative_example():
    # after a simple Greek gift sacrifice:
    # https://lichess.org/analysis/rnbq1r1k/ppp1npp1/4p3/b2pP1N1/3P4/2P5/PP3PPP/RNBQK2R_w_KQ_-_0_1
    fen = 'rnbq1r1k/ppp1npp1/4p3/b2pP1N1/3P4/2P5/PP3PPP/RNBQK2R w KQ - 2 9'
    pv = "['d1h5', 'h8g8', 'h5h7']"

    f = features.Checkmate(fen, pv)
    assert f.features()['is_smothered_mate'] == 0


def test_from_df():
    df = pd.DataFrame([{
        'fen': chess.STARTING_FEN,
        'best_move': 'e2e4',
        'best_pv': "['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5', 'a7a6', 'b5c6', 'd7c6']",
    }])

    for feature_class in [features.Board, features.PieceCount, features.BestMove, features.BestPV]:
        feature_df = feature_class.from_df(df)
