import chess

import board


def creates_hanging_piece_threat_capture(fen: str, move: chess.Move) -> bool:
    aug = board.AugBoard(fen)

    if aug.has_hanging_piece_capture():
        return False

    aug.push(move)
    aug.push(chess.Move.null())
    return aug.has_hanging_piece_capture()


def creates_material_gain_capture(fen: str, move: chess.Move) -> bool:
    aug = board.AugBoard(fen)

    if aug.has_positive_see_capture():
        return False

    aug.push(move)
    aug.push(chess.Move.null())
    return aug.has_positive_see_capture()
