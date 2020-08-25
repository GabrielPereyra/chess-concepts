import os
import subprocess
from functools import cached_property

import chess
import chess.engine
import click
import pandas as pd
from chess.engine import _parse_uci_info

from features.abstract import Features

STOCKFISH_PATH = os.environ.get("STOCKFISH_PATH", "../Stockfish/src/stockfish")
EVAL_STOCKFISH_PATH = os.environ.get("EVAL_STOCKFISH_PATH", "../Stockfish\ copy/src/stockfish")


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


class StockfishDepth(Features):
    def __init__(self, fen, p):
        p.stdin.write("position fen {}\n".format(fen))
        p.stdin.write("go depth 10\n")

        board = chess.Board(fen)

        self.scores = []
        self.mates = []
        self.moves = []
        self.pvs = []
        for line in iter(p.stdout.readline, ""):
            if "bestmove" in line:
                break

            info = _parse_uci_info(line.strip(), board)

            self.scores.append(info["score"].relative.score())
            self.mates.append(info["score"].relative.mate())
            self.moves.append(info["pv"][0].uci())
            self.pvs.append(str([move.uci() for move in info["pv"]]))

    @classmethod
    def from_row(cls, row, p):
        return cls(row.fen, p)

    @classmethod
    def from_df(cls, df):
        p = subprocess.Popen(
            STOCKFISH_PATH,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )
        p.stdout.readline()  # read info line on init.

        feature_rows = []
        with click.progressbar(tuple(df.itertuples())) as rows:
            for row in rows:
                feature_instance = cls.from_row(row, p)
                feature_rows.append(feature_instance.features())

        p.kill()
        return pd.DataFrame(feature_rows)

    @cached_property
    def scores(self):
        return self.scores

    @cached_property
    def mates(self):
        return self.mates

    @cached_property
    def moves(self):
        return self.moves

    @cached_property
    def pvs(self):
        return self.pvs


class StockfishEval(Features):
    def __init__(self, fen, p):

        print(fen)

        board = chess.Board(fen)
        p.stdin.write("position fen {}\n".format(fen))
        p.stdin.write("eval\n")

        def _parse_score(score):
            if score == "----":
                return None
            else:
                return float(score)

        for i, line in enumerate(iter(p.stdout.readline, "")):

            print(line)

            if "Total evaluation: none (in check)" in line:
                # p.stdout.readline()
                break

            if "Total evaluation" in line:
                p.stdout.readline()
                break

            if i >= 3 and i <= 15:
                term, white, black, total = line.split("|")
                term = term.strip().lower()
                white_mg, white_eg = white.split()
                black_mg, black_eg = black.split()
                total_mg, total_eg = total.split()

                white_mg = _parse_score(white_mg)
                white_eg = _parse_score(white_eg)
                black_mg = _parse_score(black_mg)
                black_eg = _parse_score(black_eg)
                total_mg = _parse_score(total_mg)
                total_eg = _parse_score(total_eg)

                # TODO: how to make these properties
                if board.turn == chess.WHITE:
                    setattr(self, "our_{}_mg".format(term), white_mg)
                    setattr(self, "our_{}_eg".format(term), white_eg)
                    setattr(self, "their_{}_mg".format(term), black_mg)
                    setattr(self, "their_{}_eg".format(term), black_eg)
                    setattr(self, "total_{}_mg".format(term), total_mg)
                    setattr(self, "total_{}_eg".format(term), total_eg)
                else:
                    setattr(self, "our_{}_mg".format(term), black_mg)
                    setattr(self, "our_{}_eg".format(term), black_eg)
                    setattr(self, "their_{}_mg".format(term), white_mg)
                    setattr(self, "their_{}_eg".format(term), white_eg)
                    setattr(self, "total_{}_mg".format(term), -total_mg)
                    setattr(self, "total_{}_eg".format(term), -total_eg)

    # TODO: create stockfish pipe class so we can share this with StockfishDepth
    @classmethod
    def from_row(cls, row, p):
        return cls(row.fen, p)

    @classmethod
    def from_df(cls, df):
        p = subprocess.Popen(
            STOCKFISH_PATH,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )
        p.stdout.readline()  # read info line on init.

        feature_rows = []
        with click.progressbar(tuple(df.itertuples())) as rows:
            for row in rows:
                feature_instance = cls.from_row(row, p)
                feature_rows.append(feature_instance.features())

        p.kill()
        return pd.DataFrame(feature_rows)


# TODO: disgusting hack because feature class expects dir(cls) to expose all features which only works if they are defined as methods but for StockfishEval, we set them all as attributes in __init__. Need to think about how to refactor this.
for feature in [
    "our_bishops_eg",
    "our_bishops_mg",
    "our_imbalance_eg",
    "our_imbalance_mg",
    "our_initiative_eg",
    "our_initiative_mg",
    "our_king safety_eg",
    "our_king safety_mg",
    "our_knights_eg",
    "our_knights_mg",
    "our_material_eg",
    "our_material_mg",
    "our_mobility_eg",
    "our_mobility_mg",
    "our_passed_eg",
    "our_passed_mg",
    "our_pawns_eg",
    "our_pawns_mg",
    "our_queens_eg",
    "our_queens_mg",
    "our_rooks_eg",
    "our_rooks_mg",
    "our_space_eg",
    "our_space_mg",
    "our_threats_eg",
    "our_threats_mg",
    "their_bishops_eg",
    "their_bishops_mg",
    "their_imbalance_eg",
    "their_imbalance_mg",
    "their_initiative_eg",
    "their_initiative_mg",
    "their_king safety_eg",
    "their_king safety_mg",
    "their_knights_eg",
    "their_knights_mg",
    "their_material_eg",
    "their_material_mg",
    "their_mobility_eg",
    "their_mobility_mg",
    "their_passed_eg",
    "their_passed_mg",
    "their_pawns_eg",
    "their_pawns_mg",
    "their_queens_eg",
    "their_queens_mg",
    "their_rooks_eg",
    "their_rooks_mg",
    "their_space_eg",
    "their_space_mg",
    "their_threats_eg",
    "their_threats_mg",
    "total_bishops_eg",
    "total_bishops_mg",
    "total_imbalance_eg",
    "total_imbalance_mg",
    "total_initiative_eg",
    "total_initiative_mg",
    "total_king safety_eg",
    "total_king safety_mg",
    "total_knights_eg",
    "total_knights_mg",
    "total_material_eg",
    "total_material_mg",
    "total_mobility_eg",
    "total_mobility_mg",
    "total_passed_eg",
    "total_passed_mg",
    "total_pawns_eg",
    "total_pawns_mg",
    "total_queens_eg",
    "total_queens_mg",
    "total_rooks_eg",
    "total_rooks_mg",
    "total_space_eg",
    "total_space_mg",
    "total_threats_eg",
    "total_threats_mg",
]:
    setattr(StockfishEval, feature, None)

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
