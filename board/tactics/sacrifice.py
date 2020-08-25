import chess

import board


def is_sacrifice_see(fen: str, move: chess.Move) -> bool:
    """
    A move is a sacrifice when it loses material.

    NOTE: Wikipedia proposed a division between sham and real sacrifices:
    https://en.wikipedia.org/wiki/Sacrifice_(chess)#Types_of_sacrifice
    maybe something to consider for the future.
    """

    aug = board.AugBoard(fen)
    return aug.see(move.to_square, attacker=move.from_square, moves_without_stop=1) < 0
