from enum import IntEnum
from typing import Dict, Callable

import chess

import board


def has_pawn_structure(fen, white_files, black_files) -> bool:
    aug = board.AugBoard(fen)
    white_pawns = aug.pieces(chess.PAWN, chess.WHITE)
    black_pawns = aug.pieces(chess.PAWN, chess.BLACK)

    for color_files, color_pawns in zip(
        [white_files, black_files], [white_pawns, black_pawns]
    ):
        for file_name, ranks in color_files.items():
            file_idx = ord(file_name) - ord("a")
            present = color_pawns & chess.SquareSet(chess.BB_FILES[file_idx])
            expected = chess.SquareSet([8 * (rank - 1) + file_idx for rank in ranks])
            if present != expected:
                return False
    return True


class PawnStructure(IntEnum):
    """
    The assumption is that if there are two pawn structures such that one is a more specialized
    variant of the other, then the more specialized one has greater integer value assigned.
    E.g. Maroczy bind vs. Hedgehog, or Closed Sicilian vs. Botvinnik System

    pawn structures source:
    https://en.wikipedia.org/wiki/Pawn_structure#The_major_pawn_formations
    """

    NONE = 0
    CARO = 1
    SLAV = 2
    SICILIAN_SCHEVENINGEN = 3
    SICILIAN_DRAGON = 4
    SICILIAN_BOLESLAVSKY_HOLE = 5
    MAROCZY_BIND = 6
    HEDGEHOG = 7
    RAUZER_FORMATION = 8
    BOLESLAVSKY_WALL = 9
    D5_CHAIN = 10
    E5_CHAIN = 11
    MODERN_BENONI = 12
    GIUOCO_PIANO_ISOLANI = 13
    QUEENS_GAMBIT_ISOLANI = 14
    HANGING_PAWNS = 15
    CARLSBAD = 16
    PANOV = 17
    STONEWALL = 18
    CLOSED_SICILIAN = 19
    BOTVINNIK_SYSTEM = 20

    @classmethod
    def detectors(cls) -> Dict["PawnStructure", Callable[[str], bool]]:
        return {
            cls.CARO: lambda fen: has_pawn_structure(
                fen,
                white_files={"d": [4], "e": []},
                black_files={"c": [6], "d": [], "e": [6]},
            ),
            cls.SLAV: lambda fen: has_pawn_structure(
                fen,
                white_files={"c": [], "d": [4], "e": [3]},
                black_files={"c": [6], "d": [], "e": [6]},
            ),
            cls.SICILIAN_SCHEVENINGEN: lambda fen: has_pawn_structure(
                fen,
                white_files={"d": [], "e": [4]},
                black_files={"c": [], "d": [6], "e": [6]},
            ),
            cls.SICILIAN_DRAGON: lambda fen: has_pawn_structure(
                fen,
                white_files={"d": [], "e": [4]},
                black_files={"c": [], "d": [6], "g": [6]},
            ),
            cls.SICILIAN_BOLESLAVSKY_HOLE: lambda fen: has_pawn_structure(
                fen,
                white_files={"d": [], "e": [4]},
                black_files={"c": [], "d": [6], "e": [5]},
            ),
            cls.MAROCZY_BIND: lambda fen: has_pawn_structure(
                fen, white_files={"c": [4], "d": [], "e": [4]}, black_files={"c": []},
            ),
            cls.HEDGEHOG: lambda fen: has_pawn_structure(
                fen,
                white_files={"c": [4], "d": [], "e": [4]},
                black_files={"a": [6], "b": [6], "c": [], "d": [6], "e": [6]},
            ),
            cls.RAUZER_FORMATION: lambda fen: has_pawn_structure(
                fen,
                white_files={"c": [4], "d": [], "e": [4]},
                black_files={"c": [6], "d": [], "e": [5]},
            ),
            cls.BOLESLAVSKY_WALL: lambda fen: has_pawn_structure(
                fen,
                white_files={"c": [4], "d": [], "e": [4]},
                black_files={"c": [6], "d": [6], "e": []},
            ),
            cls.D5_CHAIN: lambda fen: has_pawn_structure(
                fen, white_files={"d": [5], "e": [4]}, black_files={"d": [6], "e": [5]},
            ),
            cls.E5_CHAIN: lambda fen: has_pawn_structure(
                fen, white_files={"d": [4], "e": [5]}, black_files={"d": [5], "e": [6]},
            ),
            cls.MODERN_BENONI: lambda fen: has_pawn_structure(
                fen,
                white_files={"c": [], "d": [5], "e": [4]},
                black_files={"c": [5], "d": [6], "e": []},
            ),
            cls.GIUOCO_PIANO_ISOLANI: lambda fen: has_pawn_structure(
                fen,
                white_files={"c": [], "d": [4], "e": []},
                black_files={"d": [], "e": []},
            ),
            cls.QUEENS_GAMBIT_ISOLANI: lambda fen: has_pawn_structure(
                fen,
                white_files={"c": [], "d": [4], "e": []},
                black_files={"c": [], "d": [], "e": [6]},
            ),
            cls.HANGING_PAWNS: lambda fen: has_pawn_structure(
                fen,
                white_files={"b": [], "c": [4], "d": [4], "e": []},
                black_files={"c": [], "d": [], "e": [6]},
            ),
            cls.CARLSBAD: lambda fen: has_pawn_structure(
                fen,
                white_files={"c": [], "d": [4], "e": [3]},
                black_files={"c": [6], "d": [5], "e": []},
            ),
            cls.PANOV: lambda fen: has_pawn_structure(
                fen,
                white_files={"c": [5], "d": [4], "e": []},
                black_files={"c": [], "d": [5], "e": [6]},
            ),
            cls.STONEWALL: lambda fen: has_pawn_structure(
                fen,
                white_files={"d": [4], "e": [3], "f": [4]},
                black_files={"d": [5], "e": [6], "f": [5]},
            ),
            cls.BOTVINNIK_SYSTEM: lambda fen: has_pawn_structure(
                fen,
                white_files={"c": [4], "d": [3], "e": [4]},
                black_files={"c": [5], "d": [6], "e": [5]},
            ),
            cls.CLOSED_SICILIAN: lambda fen: has_pawn_structure(
                fen, white_files={"d": [3], "e": [4]}, black_files={"c": [5], "d": [6]},
            ),
        }
