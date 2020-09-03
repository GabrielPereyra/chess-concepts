from functools import cached_property

import chess

from features.abstract import Features


class Clock(Features):
    """Features relating to time control and game clock. """

    def __init__(self, time_control_string, clock):
        self.time_control_string = time_control_string
        self.clock = clock

    @classmethod
    def from_row(cls, row):
        return cls(row.time_control_string, row.clock)

    @cached_property
    def approximate_game_length(self):
        """Approximate game length in seconds (T = S + 40 * I) where S is the starting time and I is the increment"""
        # https://lichess.org/forum/general-chess-discussion/is-there-any-data-or-statistics-that-shows

        # TODO: why are some games missing time_controls?
        if self.time_control_string == "-":
            return None

        s, i = self.time_control_string.split("+")
        s = int(s)
        i = int(i)
        return s + i * 40

    @cached_property
    def relative_time_remaining(self):
        """Clock divided by approximate game length."""
        if self.time_control_string == "-":
            return None

        return self.clock / self.approximate_game_length

    # TODO: rename lichess time-control to time-control-string?
    @cached_property
    def time_control_name(self):
        if self.time_control_string == "-":
            return None
        s, i = self.time_control_string.split("+")
        s = int(s)
        if s < 30:
            return "ultra"
        if s < 180:
            return "bullet"
        if s < 480:
            return "blitz"
        if s < 1200:
            return "rapid"
        else:
            return "classical"
