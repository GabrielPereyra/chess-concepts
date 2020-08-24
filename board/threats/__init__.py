import chess

from board import AugBoard


def creates_mate_threat(fen: str, move: chess.Move) -> bool:
    aug = AugBoard(fen)

    if aug.has_mate():
        return False

    aug.push(move)
    aug.push(chess.Move.null())
    return aug.has_mate()


def creates_capture_handing_piece_threat(fen: str, move: chess.Move) -> bool:
    aug = AugBoard(fen)

    if aug.has_hanging_piece_capture():
        return False

    aug.push(move)
    aug.push(chess.Move.null())
    return aug.has_hanging_piece_capture()


def creates_positive_see_capture(fen: str, move: chess.Move) -> bool:
    aug = AugBoard(fen)

    if aug.has_positive_see_capture():
        return False

    aug.push(move)
    aug.push(chess.Move.null())
    return aug.has_positive_see_capture()
