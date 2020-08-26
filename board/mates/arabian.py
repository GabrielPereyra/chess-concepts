import chess

import board


def is_arabian_mate_classic(fen: str, move: chess.Move):
    """
    According to Wikipedia:
    > In the Arabian mate, the knight and the rook team up to trap the opposing king on a corner of the board.
    > The rook sits on a square adjacent to the king both to prevent escape along the diagonal and to deliver checkmate
    > while the knight sits two squares away diagonally from the king to prevent escape on the square next to the king
    > and to protect the rook.
    source: https://en.wikipedia.org/wiki/Checkmate_pattern#Arabian_mate
    """

    aug = board.AugBoard(fen)

    their_king = aug.other_color_king()

    if any(
        (
            their_king is None,
            (chess.BB_SQUARES[their_king] & chess.BB_CORNERS) == chess.BB_EMPTY,
            aug.piece_type_at(move.from_square) != chess.ROOK,
        )
    ):
        return False

    aug.push(move)

    if not aug.is_checkmate():
        return False

    patterns = {
        chess.A1: ([chess.A2, chess.B1], chess.C3),
        chess.H1: ([chess.H2, chess.G1], chess.F3),
        chess.A8: ([chess.A7, chess.B8], chess.C6),
        chess.H8: ([chess.H7, chess.G8], chess.F6),
    }

    rook_squares, knight_square = patterns[their_king]
    return move.to_square in rook_squares and aug.piece_at(
        knight_square
    ) == chess.Piece(chess.KNIGHT, aug.other_color)


def is_arabian_mate_extra_extended(fen: str, move: chess.Move):
    """
    Same as in Wikipedia definition except that King can be on any square.
    """

    aug = board.AugBoard(fen)

    king = aug.other_color_king()

    if any((king is None, aug.piece_type_at(move.from_square) != chess.ROOK,)):
        return False

    aug.push(move)

    if not aug.is_checkmate():
        return False

    rook = move.to_square

    if chess.square_distance(king, rook) > 1 or king not in aug.attacks(rook):
        return False

    knights_defending_rook = [
        square
        for square in aug.attackers(aug.other_color, rook)
        if aug.piece_type_at(square) == chess.KNIGHT
    ]
    if not knights_defending_rook:
        return False

    escape_squares = [
        square for square in aug.attacks(king) if aug.piece_at(square) is None
    ]
    for escape_square in escape_squares:
        if not aug.attackers(aug.other_color, escape_square):
            return False

    return True


def is_arabian_mate_extended(fen: str, move: chess.Move):
    """
    Same as in Wikipedia definition except that King can be on any border square.
    """
    aug = board.AugBoard(fen)

    king = aug.other_color_king()

    if (chess.square_file(king) not in [0, 7]) and (
        chess.square_rank(king) not in [0, 7]
    ):
        return False

    return is_arabian_mate_extra_extended(fen, move)
