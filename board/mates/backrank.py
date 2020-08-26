import chess

import board


def is_back_rank_mate(fen, move):
    """
    According to Wikipedia:
    > In chess, a back-rank checkmate (also known as the corridor mate) is a checkmate delivered by a rook or queen
    > along a back rank (that is, the row on which the pieces [not pawns] stand at the start of the game) in which
    > the mated king is unable to move up the board because the king is blocked by friendly pieces (usually pawns)
    > on the second rank.
    source: https://en.wikipedia.org/wiki/Back-rank_checkmate
    """

    aug = board.AugBoard(fen)
    their_back_rank = 7 if aug.other_color == chess.BLACK else 0

    their_king = aug.other_color_king()

    if any(
        (
            their_king is None,
            chess.square_rank(their_king) != their_back_rank,
            chess.square_rank(move.to_square) != their_back_rank,
        )
    ):
        return False

    aug.push(move)

    if any(
        (
            not aug.is_checkmate(),
            aug.piece_type_at(move.to_square) not in [chess.QUEEN, chess.ROOK],
        )
    ):
        return False

    num_friendly_blocking_pieces = 0
    for square in aug.attacks(their_king) - aug.attacks(move.to_square):
        if chess.square_rank(square) == their_back_rank:
            continue
        if bool(aug.attackers(aug.other_color, square)):
            continue
        piece = aug.piece_at(square)
        if piece is None or piece.color != aug.current_color:
            return False
        else:
            num_friendly_blocking_pieces += 1
    return num_friendly_blocking_pieces > 0
