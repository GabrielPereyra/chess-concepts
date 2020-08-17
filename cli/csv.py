import os
import math
import utils
import click
import chess
import chess.pgn
import chess.engine
import pandas as pd
import datetime
import features

LICHESS_PGN_PATH = "pgns/lichess_db_standard_rated_{year}-{month:0>2}.pgn"
LICHESS_CSV_PATH = "csvs/lichess/{year}-{month:0>2}/"
FEATURE_CSV_PATH = "csvs/{feature_name}/{year}-{month:0>2}/"
SHARD_SIZE = 100000
os.makedirs("csvs", exist_ok=True)
os.makedirs("pgns", exist_ok=True)


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
            cp *= 1 if score.mate() > 0 else -1
        else:
            cp = min(max(-1000, score.cp), 1000)
        return 2 / (1 + math.exp(-0.004 * cp)) - 1

    winning_chances = score_to_winning_chances(score)
    prev_winning_chances = score_to_winning_chances(prev_score)
    winning_chances_loss = -(winning_chances - prev_winning_chances) / 2

    if winning_chances_loss < 0.025:
        move_evaluation_type = 0 # correct
    elif winning_chances_loss < 0.06:
        move_evaluation_type = 1 # inaccurate
    elif winning_chances_loss < 0.14:
        move_evaluation_type = 2 # mistake
    else:
        move_evaluation_type = 3 # blunder

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
        }

        row.update(winning_chances(score, prev_score, board.turn))
        row.update(metrics(score, prev_score, board.turn))
        rows.append(row)
        board.push(move)

        prev_move = move.uci()
        prev_score = score

    return rows


def write_shard(rows, csv_path, shard):
    df = pd.DataFrame(rows)
    df.to_csv(csv_path + str(shard) + ".csv", index=False)
    print("wrote shard {}".format(shard))


def lichess_month_pgn_to_csv(year, month):
    csv_path = LICHESS_CSV_PATH.format(year=year, month=month)
    pgn_path = LICHESS_PGN_PATH.format(year=year, month=month)
    os.makedirs(csv_path, exist_ok=True)
    pgn = open(pgn_path)

    games = 0
    games_with_eval = 0
    shard = 0
    rows = []
    while True:
        game = chess.pgn.read_game(pgn)
        if game is None:
            break
        games += 1

        mainline = tuple(game.mainline())
        if not mainline or mainline[0].eval() is None:
            continue

        games_with_eval += 1

        if game is None:
            break
        if game.headers["WhiteElo"] == "?":
            continue
        if game.headers["BlackElo"] == "?":
            continue
        rows.extend(game_to_rows(game))

        if len(rows) > SHARD_SIZE:
            write_shard(rows, csv_path, shard)
            rows = []
            shard += 1

        if games_with_eval % 100 == 0:
            print(games, games_with_eval, len(rows))

    write_shard(rows, csv_path, shard)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("year", type=int)
@click.argument("month", type=int)
def lichess(year, month):
    """Convert lichess month pgn to csv. Expects a pgn file in the pgns/ dir formatted lichess_db_standard_rated_{year}-{month}.pgn. You can download these from https://database.lichess.org/."""
    lichess_month_pgn_to_csv(year, month)


@cli.command()
@click.argument("year")
@click.argument("month")
@click.argument("feature_name")
@click.option("--num_shards", type=int, help="number of shards to use.")
def feature(year, month, feature_name, num_shards):
    """
    Generate feature csvs for all shards in csvs/{year}-{month}.

    year: year of lichess pgn.

    month: month of lichess pgn.

    feature_name: class name of feature.
    """

    # TODO: handle case where user passes a lowercase feature name.

    path = LICHESS_CSV_PATH.format(year=year, month=month)
    if num_shards is None:
        num_shards = len(os.listdir(path))

    feature_class = getattr(features, feature_name)
    feature_dir = FEATURE_CSV_PATH.format(
        feature_name=feature_name.lower(), year=year, month=month
    )
    os.makedirs(feature_dir, exist_ok=True)
    for shard in range(num_shards):
        df = utils.get_df(feature_class.csvs, years=[year], months=[month], shard=shard)
        feature_df = feature_class.from_df(df)
        feature_df.to_csv(feature_dir + str(shard) + ".csv", index=False)
        print("wrote shard {}".format(shard))


if __name__ == "__main__":
    cli()
