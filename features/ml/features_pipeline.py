import chess.engine

from features import BestMove, BestPV, Board, Checkmate, CheckmateType, Motives
from features.ml.bitboards import BitBoards
from features.stockfish import Stockfish


def extract_all_features(
        fen, engine_path, engine_process=None, depth=None, multipv=None
):
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    try:
        stockfish = Stockfish(fen, engine, depth, multipv)
        best_move = stockfish.best_move
        best_pv = stockfish.best_pv
    except:
        print(f"Stockfish error analysing position {fen}")

    try:
        features = extract_all_features_precalc(fen, best_move, best_pv)
    except:
        print("error")

    engine.close()

    return features


def extract_all_features_precalc(
        fen, best_move, best_pv, engine_process=None
):
    feature_sets = [
        BestMove(fen, best_move),
        BestPV(fen, best_pv),
        Board(fen),
        Checkmate(fen, best_pv),
        CheckmateType(fen, best_pv),
        Motives(fen, best_pv),
        BitBoards(fen)
    ]

    features = {}
    for feature_set in feature_sets:
        prefix = feature_set.__class__.__name__
        for k, v in feature_set.features().items():
            # convert enums
            if hasattr(v, "name"):
                v = v.name
            if k.endswith("_piece_type") and v in range(1, 7):
                v = chess.piece_name(v)
            # explode list - encode the elements as binary values
            if isinstance(v, list):
                for el in v:
                    features[f"{prefix}_{k}={el}"] = 1
            else:
                features[f"{prefix}_{k}"] = v

    return features
