import chess

import board


def creates_mate_threat(fen: str, move: chess.Move) -> bool:
    aug = board.AugBoard(fen)

    if aug.gives_check(move):
        return False

    if aug.has_mate():
        return False

    aug.push(move)
    aug.push(chess.Move.null())
    return aug.has_mate()
