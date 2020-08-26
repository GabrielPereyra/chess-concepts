from enum import IntEnum
from typing import Dict, Callable
from collections import Counter

import chess

from .smothered import is_smothered_mate
from .backrank import is_back_rank_mate
from .arabian import is_arabian_mate_extended as is_arabian_mate
from .mating_net import is_mate_with_pieces


# TODO: consider refactoring to enum.IntFlag if we want them to behave like bit flags
# https://docs.python.org/3/library/enum.html#intflag
class CheckmateType(IntEnum):
    NONE = 0
    BACK_RANK = 1
    SMOTHERED = 2
    ARABIAN = 3

    # piece combinations taken from: https://en.wikipedia.org/wiki/Checkmate
    QUEEN_ROOK = 4
    ROOK_ROOK = 5
    KING_QUEEN = 6
    KING_ROOK = 7
    KING_BISHOP_BISHOP = 8
    KING_BISHOP_KNIGHT = 9

    @classmethod
    def detectors(cls) -> Dict["CheckmateType", Callable[[str, chess.Move], bool]]:
        return {
            cls.BACK_RANK: is_back_rank_mate,
            cls.SMOTHERED: is_smothered_mate,
            cls.ARABIAN: is_arabian_mate,
            cls.QUEEN_ROOK: lambda fen, move: is_mate_with_pieces(
                fen, move, Counter((chess.QUEEN, chess.ROOK))
            ),
            cls.ROOK_ROOK: lambda fen, move: is_mate_with_pieces(
                fen, move, Counter((chess.ROOK, chess.ROOK))
            ),
            cls.KING_QUEEN: lambda fen, move: is_mate_with_pieces(
                fen, move, Counter((chess.KING, chess.QUEEN))
            ),
            cls.KING_ROOK: lambda fen, move: is_mate_with_pieces(
                fen, move, Counter((chess.KING, chess.ROOK))
            ),
            cls.KING_BISHOP_BISHOP: lambda fen, move: is_mate_with_pieces(
                fen, move, Counter((chess.KING, chess.BISHOP, chess.BISHOP))
            ),
            cls.KING_BISHOP_KNIGHT: lambda fen, move: is_mate_with_pieces(
                fen, move, Counter((chess.KING, chess.BISHOP, chess.KNIGHT))
            ),
        }
