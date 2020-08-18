from functools import cached_property

import chess

from features.abstract import Features


class Opening(Features):
    def __init__(self, opening):
        self.opening = opening

    @classmethod
    def from_row(cls, row):
        return cls(row.opening)

    @cached_property
    def opening_name(self):
        opening = self.opening
        if ":" in opening:
            opening = self.opening.split(":")[0]
        if "#" in opening:
            opening = opening.split("#")[0]
        opening = opening.strip()
        return opening
