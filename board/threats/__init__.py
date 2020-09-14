from enum import IntEnum
from typing import Dict, Callable

import chess

import board
from .capture import creates_hanging_piece_threat_capture, creates_material_gain_capture
from .mate import creates_mate_threat


def make_tactic_threat_detector(tactic: board.Tactic):
    def detector(fen: str, move: chess.Move):
        aug = board.AugBoard(fen)

        # TODO: do we want to exclude checks?
        if aug.gives_check(move):
            return False

        aug.push(move)
        aug.push(chess.Move.null())
        return any(
            tactic in aug.move_tactics(next_move) for next_move in aug.legal_moves
        )

    return detector


# TODO: consider refactoring to enum.IntFlag if we want them to behave like bit flags
# https://docs.python.org/3/library/enum.html#intflag
class Threat(IntEnum):
    NONE = 0
    MATE = 1
    HANGING_PIECE_CAPTURE = 2
    MATERIAL_GAIN_CAPTURE = 3
    DISCOVERED_ATTACK = 4
    FORK = 5
    SKEWER = 6
    # TODO: PIN should rather not be there - is it a valid assumption?
    # TODO: For SACRIFICE on one hand it makes sense (e.g. threat to make greek gift) but on the other it does not
    #  because for us sacrifice only makes sense when it is a good move as otherwise moving a piece so that it
    #  is hanging will also be classified as a sacrifice which is fine but having a threat of doing this
    #  does not make much sense

    @classmethod
    def detectors(cls) -> Dict["Threat", Callable[[str, chess.Move], bool]]:
        return {
            cls.MATE: creates_mate_threat,
            cls.HANGING_PIECE_CAPTURE: creates_hanging_piece_threat_capture,
            cls.MATERIAL_GAIN_CAPTURE: creates_material_gain_capture,
            # cls.FORK: make_tactic_threat_detector(board.Tactic.FORK),
            # cls.DISCOVERED_ATTACK: make_tactic_threat_detector(
            #     board.Tactic.DISCOVERED_ATTACK
            # ),
            # cls.SKEWER: make_tactic_threat_detector(board.Tactic.SKEWER),
        }

    @classmethod
    def detector(cls, threat: "Threat") -> Callable[[str, chess.Move], bool]:
        return cls.detectors()[threat]
