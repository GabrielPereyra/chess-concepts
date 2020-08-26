import board


def is_smothered_mate(fen, move):
    """
    According to Wikipedia:
    > In chess, a smothered mate is a checkmate delivered by a knight in which the mated king is unable to move
    > because he is surrounded (or smothered) by his own pieces.
    source: https://en.wikipedia.org/wiki/Smothered_mate
    """

    aug = board.AugBoard(fen)
    aug.push(move)
    if not aug.is_checkmate():
        return False
    their_king = aug.current_color_king()
    for square in aug.attacks(their_king):
        piece = aug.piece_at(square)
        if piece is None or piece.color != aug.current_color:
            return False
    return True
