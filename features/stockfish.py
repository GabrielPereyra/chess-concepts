from functools import cached_property

import click
import chess
import chess.engine
import pandas as pd

from features.abstract import Features

STOCKFISH_PATH = "../Stockfish/src/stockfish"


def stockfish_info(fen, move, engine, depth, multipv=None):
    board = chess.Board(fen)
    move = [chess.Move.from_uci(move)] if move else None
    return engine.analyse(
        board, root_moves=move, multipv=multipv, limit=chess.engine.Limit(depth=depth)
    )


class Stockfish(Features):

    # TODO: create a stockfish class that uses popen and catches all depth evals and best moves.
    # TODO: add a version that takes users move and analyzes it.
    def __init__(self, fen, engine, depth, multipv):
        self.info = stockfish_info(
            fen=fen, move=None, engine=engine, depth=depth, multipv=multipv,
        )

    @classmethod
    def from_row(cls, row, engine):
        return cls(row.fen, engine)

    @classmethod
    def from_df(cls, df):
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

        feature_rows = []
        with click.progressbar(tuple(df.itertuples())) as rows:
            for row in rows:
                feature_instance = cls.from_row(row, engine)
                feature_rows.append(feature_instance.features())

        engine.quit()
        return pd.DataFrame(feature_rows)

    @cached_property
    def best_score(self):
        return self.info["score"].relative.score()

    @cached_property
    def best_mate(self):
        return self.info["score"].relative.mate()

    @cached_property
    def best_move(self):
        return self.info["pv"][0].uci()

    @cached_property
    def best_pv(self):
        return str([move.uci() for move in self.info["pv"]])


class Stockfish10(Stockfish):
    def __init__(self, fen, engine):
        super().__init__(fen, engine, 10, None)


# TODO: how to store scores and pvs?
# class Stockfish5_500(Stockfish):
#     def __init__(self, fen, engine):
#         super().__init__(fen, engine, 5, 500)


# def get_modified_stockfish_process():
#     p = subprocess.Popen(
#         STOCKFISH_PATH_MODIFIED,
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         universal_newlines=True,
#         bufsize=1
#     )
#     p.stdout.readline() # read info line on init.
#     return p
#
#
#
# p.kill()


# # TODO: move this to stockfish?
# def read_remaining_lines(p):
#     for line in iter(p.stdout.readline, ''):
#         if 'done' in line:
#             break
#
#
# def parse_lines(p):
#     lines = []
#     for line in iter(p.stdout.readline, ''):
#         if line.startswith('Total evaluation: none (in check)'):
#             return lines
#
#         if 'Term' in line or line.startswith('specialized_eval_exists') or line.startswith('high_score_early_exit'):
#             read_remaining_lines(p)
#             return lines
#
#         lines.append(line.split())
#
#     # TODO: should we ever get here?
#     raise ValueError()


# def stockfish_eval_features(fen, p):
#
#     # TODO: should we use this? Useful for debugging (move to test?).
#     feature_names = [
#
#         # piece features
#         'knight_outpost',
#         'bishop_outpost',
#         'reachable_outpost',
#         'knight_behind_pawn',
#         'bishop_behind_pawn',
#         'knight_distance_from_king',
#         'bishop_distance_from_king',
#         'bishop_pawns_on_same_color',
#         'bishop_xray_pawns',
#         'long_diagonal_bishop',
#         'rook_on_queen_file',
#         'rook_on_file',
#         'trapped_rook',
#         'weak_queen',
#
#         # threats
#         'strongly_protected_squares',
#         'strongly_protected_non_pawn_pieces',
#         'weak_pieces',
#         'hanging_pieces',
#         'weak_queen_protection',
#         'restricted_pieces',
#         'safe_squares',
#         'threat_by_safe_pawns',
#         'threat_by_pawn_pushes',
#         'knight_on_queen',
#         'slider_on_queen',
#
#         # king
#         'safe_rook_checks',
#         'safe_queen_checks',
#         'safe_bishop_checks',
#         'safe_knight_checks',
#         'unsafe_checks',
#         'king_attackers',
#         'weak_king_ring',
#         'king_attacks',
#
#         # pawns
#     ]
#
#     features = collections.defaultdict(int)
#
#     for feature_name in feature_names:
#         for prefix in ['our', 'their']:
#             features['{}_{}'.format(prefix, feature_name)] = 0
#
#     p.stdin.write('position fen {}\n'.format(fen))
#     p.stdin.write('eval\n')
#
#     lines = parse_lines(p)
#
#     for turn, feature_name, feature_value in lines:
#         if feature_name in feature_names:
#             prefix = 'our' if turn == '1' else 'their'
#             features['{}_{}'.format(prefix, feature_name)] += int(feature_value)
#
#     return features
