from enum import IntEnum
from typing import Dict, Callable

import chess

from .capture import creates_hanging_piece_threat_capture, creates_material_gain_capture
from .mate import creates_mate_threat


# TODO: consider refactoring to enum.IntFlag if we want them to behave like bit flags
# https://docs.python.org/3/library/enum.html#intflag
class Threat(IntEnum):
    NONE = 0
    MATE = 1
    HANGING_PIECE_CAPTURE = 2
    MATERIAL_GAIN_CAPTURE = 3

    @classmethod
    def detectors(cls) -> Dict["Threat", Callable[[str, chess.Move], bool]]:
        return {
            cls.MATE: creates_mate_threat,
            cls.HANGING_PIECE_CAPTURE: creates_hanging_piece_threat_capture,
            cls.MATERIAL_GAIN_CAPTURE: creates_material_gain_capture,
        }

    @classmethod
    def detector(cls, threat: "Threat") -> Callable[[str, chess.Move], bool]:
        return cls.detectors()[threat]
