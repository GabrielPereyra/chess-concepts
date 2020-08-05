import math
import chess
import chess.pgn
import chess.engine
import itertools
import datetime
import pandas as pd
S3_PATH = 's3://chess-puzzles/single-best-mate/{year}-{month:0>2}/{shard}.csv'


def get_df(years=[2013], months=[1]):
    dfs = []
    for year in years:
        for month in months:
            for shard in itertools.count():
                path = S3_PATH.format(year=year, month=month, shard=shard)
                try:
                    df = pd.read_csv(path)
                    print(path)
                except Exception as e:
                    print(e)
                    break

                df = df.dropna(how='all')
                dfs.append(df)
    return pd.concat(dfs).reset_index(drop=True)


def metrics(score, prev_score, turn):
    if prev_score is None: return {}
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
                assert prev_score.is_mate()
                # TODO: does this handle checkmate?
                mate_loss = max(score.mate() - prev_score.mate() + 1, 0)
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
                assert prev_score.mate() > 0
                lost_mate = True
            else:
                score_loss = max(prev_score.score() - score.score(), 0)

    return {
        'score_loss': score_loss,
        'mate_loss': mate_loss,
        'into_mate': into_mate,
        'lost_mate': lost_mate,
    }


def winning_chances(score, prev_score, turn):
    if prev_score is None: return {}
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
        error_classification = 'correct'
    elif winning_chances_loss < 0.06:
        error_classification = 'inaccuracy'
    elif winning_chances_loss < 0.14:
        error_classification = 'mistake'
    else:
        error_classification = 'blunder'

    return {
        'winning_chances': winning_chances,
        'prev_winning_chances': prev_winning_chances,
        'winning_chances_loss': winning_chances_loss,
        'error_classification': error_classification
    }


def user_df(pgn_path):
    pgn = open(pgn_path)

    rows = []
    while True:
        game = chess.pgn.read_game(pgn)
        if game is None: break

        prev_move = None
        prev_score = chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE)
        board = chess.Board()
        for node in game.mainline():
            username = game.headers['White'] if board.turn else game.headers['Black']
            elo = game.headers['WhiteElo'] if board.turn else game.headers['BlackElo']
            datetime_string = game.headers['UTCDate'] + ' ' + game.headers['UTCTime']
            datetime_parsed = datetime.datetime.strptime(datetime_string, '%Y.%m.%d %H:%M:%S')

            move = node.move

            if node.board().is_checkmate():
                score = chess.engine.PovScore(chess.engine.MateGiven, board.turn)
            else:
                score = node.eval()

            row = {
                'username': username,
                'datetime': datetime_parsed,
                'opening': game.headers['Opening'],
                'eco': game.headers['ECO'],
                'game_id': game.headers['Site'].split('/')[-1],
                'time_control': game.headers['TimeControl'],
                'elo': elo,
                'fen': board.fen(),
                'move': move.uci(),
                'prev_move': prev_move,
                'score': score.pov(board.turn).score(),
                'mate': score.pov(board.turn).mate(),
                'prev_score': prev_score.pov(board.turn).score(),
                'prev_mate': prev_score.pov(board.turn).mate(),
                'clock': node.clock(),
            }

            verdict = winning_chances(score, prev_score, board.turn)
            row.update(metrics(score, prev_score, board.turn))

            print('{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}'.format(
                str(score), str(prev_score), str(row['score_loss']), str(row['mate_loss']), str(row['into_mate']), str(row['lost_mate']), str(verdict)
            ))

            rows.append(row)
            board.push(move)

            prev_move = move.uci()
            prev_score = score

    return pd.DataFrame(rows)
