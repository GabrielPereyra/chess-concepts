import math
import chess
import chess.pgn
import datetime
import pandas as pd


# CSV_PATH = "csvs/{type}/{name}/"
LICHESS_PGN_NAME = "lichess_db_standard_rated_{year}-{month:0>2}"
PGN_PATH = "pgns/{name}.pgn"
CSV_PATH = "csvs/lichess/{name}/"
FEATURE_CSV_PATH = "csvs/{feature}/{name}/"
SHARD_SIZE = 100000


def metrics(score, prev_score, turn):
    if prev_score is None:
        return {}
    score = score.pov(turn)
    prev_score = prev_score.pov(turn)

    score_loss = None
    mate_loss = None
    into_mate = False
    lost_mate = False

    if isinstance(score, chess.engine.MateGivenType):
        mate_loss = 0
    else:
        if score.is_mate():
            if score.mate() > 0:
                # TODO: when we search for positions where best move is mate, these aren't going to come up.
                if prev_score.is_mate():
                    mate_loss = max(score.mate() - prev_score.mate() + 1, 0)
                else:
                    mate_loss = 0
            else:
                if prev_score.is_mate():
                    if prev_score.mate() > 0:
                        into_mate = True
                        lost_mate = True
                    else:
                        mate_loss = max(score.mate() - prev_score.mate(), 0)
                else:
                    into_mate = True
        else:
            if prev_score.is_mate():
                if prev_score.mate() > 0:
                    lost_mate = True
                else:
                    mate_loss = 0
            else:
                score_loss = max(prev_score.score() - score.score(), 0)

    return {
        "score_loss": score_loss,
        "mate_loss": mate_loss,
        "into_mate": into_mate,
        "lost_mate": lost_mate,
    }


def winning_chances(score, prev_score, turn):
    if prev_score is None:
        return {}

    score = score.pov(turn)
    prev_score = prev_score.pov(turn)

    def score_to_winning_chances(score):
        if score.is_mate():
            cp = (21 - min(10, abs(score.mate()))) * 100
            cp *= 1 if score.mate() >= 0 else -1
        else:
            cp = min(max(-1000, score.cp), 1000)
        return 2 / (1 + math.exp(-0.004 * cp)) - 1

    winning_chances = score_to_winning_chances(score)
    prev_winning_chances = score_to_winning_chances(prev_score)
    winning_chances_loss = -(winning_chances - prev_winning_chances) / 2

    if winning_chances_loss < 0.025:
        move_evaluation_type = 0  # correct
    elif winning_chances_loss < 0.06:
        move_evaluation_type = 1  # inaccurate
    elif winning_chances_loss < 0.14:
        move_evaluation_type = 2  # mistake
    else:
        move_evaluation_type = 3  # blunder

    return {
        "winning_chances": winning_chances,
        "prev_winning_chances": prev_winning_chances,
        "winning_chances_loss": winning_chances_loss,
        "move_evaluation_type": move_evaluation_type,
    }


def game_to_rows(game):
    rows = []
    prev_move = None
    prev_score = chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE)
    board = chess.Board()
    for node in game.mainline():
        username = game.headers["White"] if board.turn else game.headers["Black"]
        elo = game.headers["WhiteElo"] if board.turn else game.headers["BlackElo"]
        datetime_string = game.headers["UTCDate"] + " " + game.headers["UTCTime"]
        datetime_parsed = datetime.datetime.strptime(
            datetime_string, "%Y.%m.%d %H:%M:%S"
        )
        won = (
            game.headers["Result"] == "1-0"
            if board.turn
            else game.headers["Result"] == "0-1"
        )

        move = node.move
        if node.board().is_checkmate():
            score = chess.engine.PovScore(chess.engine.MateGiven, board.turn)
        else:
            score = node.eval()

        # some games don't have complete evals (https://lichess.org/5Bl3kibm)
        if score is None:
            return rows

        row = {
            "elo": elo,
            "elo_bin": int(int(elo) / 100) * 100,
            "username": username,
            "datetime": datetime_parsed,
            "opening": game.headers["Opening"],
            "eco": game.headers["ECO"],
            "game_id": game.headers["Site"].split("/")[-1],
            "time_control_string": game.headers["TimeControl"],
            "fen": board.fen(),
            "move": move.uci(),
            "prev_move": prev_move,
            "score": score.pov(board.turn).score(),
            "mate": score.pov(board.turn).mate(),
            "prev_score": prev_score.pov(board.turn).score(),
            "prev_mate": prev_score.pov(board.turn).mate(),
            "clock": node.clock(),
            "won": won,
        }

        row.update(winning_chances(score, prev_score, board.turn))
        row.update(metrics(score, prev_score, board.turn))
        rows.append(row)
        board.push(move)

        prev_move = move.uci()
        prev_score = score

    return rows


def pgn_to_df(pgn, limit=None):
    rows = []
    while True:
        game = chess.pgn.read_game(pgn)
        if game is None:
            break

        mainline = tuple(game.mainline())
        if not mainline or mainline[0].eval() is None:
            continue

        if game is None:
            break
        if game.headers["Termination"] == "Abandoned":
            continue
        if game.headers["WhiteElo"] == "?":
            continue
        if game.headers["BlackElo"] == "?":
            continue

        rows.extend(game_to_rows(game))

        if len(rows) >= limit:
            return pd.DataFrame(rows)[:limit]

    return pd.DataFrame(rows)


def add_features(df, feature_classes):
    for feature_class in feature_classes:
        feature_df = feature_class.from_df(df)
        df = df.join(feature_df)
    return df