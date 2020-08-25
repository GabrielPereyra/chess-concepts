from enum import IntEnum
from typing import Dict, Callable

import chess

from .discovered_attack import is_discovered_attack_see as is_discovered_attack
from .fork import is_fork_see as is_fork
from .pin import is_pin_see as is_pin
from .sacrifice import is_sacrifice_see as is_sacrifice
from .skewer import is_skewer_see as is_skewer


# TODO: consider refactoring to enum.IntFlag if we want them to behave like bit flags
# https://docs.python.org/3/library/enum.html#intflag
class Tactic(IntEnum):
    NONE = 0
    FORK = 1
    DISCOVERED_ATTACK = 2
    PIN = 3
    SKEWER = 4
    SACRIFICE = 5

    @classmethod
    def detectors(cls) -> Dict["Tactic", Callable[[str, chess.Move], bool]]:
        return {
            cls.FORK: is_fork,
            cls.DISCOVERED_ATTACK: is_discovered_attack,
            cls.PIN: is_pin,
            cls.SKEWER: is_skewer,
            cls.SACRIFICE: is_sacrifice,
        }

    @classmethod
    def detector(cls, tactic: "Tactic") -> Callable[[str, chess.Move], bool]:
        return cls.detectors()[tactic]
