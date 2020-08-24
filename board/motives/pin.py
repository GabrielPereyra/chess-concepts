import chess

from board import AugBoard


def is_pin_see(fen: str, move: chess.Move) -> bool:
    aug = AugBoard(fen)

    if aug.piece_type_at(move.from_square) not in [
        chess.QUEEN,
        chess.ROOK,
        chess.BISHOP,
    ]:
        return False

    attackers_before_move = aug.attacking_pairs(aug.current_color)
    aug.push(move)
    if aug.is_checkmate():
        return False
    attackers_after_move = aug.attacking_pairs(aug.other_color)

    triples = []
    for attacker, attacked in attackers_after_move - attackers_before_move:
        capturers = aug.square_capturers(attacker)
        if capturers and aug.see(attacker, moves_without_stop=1) >= 0:
            continue

        without_attacked = AugBoard(aug.fen())
        without_attacked.remove_piece_at(attacked)

        for some_attacker, new_attacked in without_attacked.attacking_pairs(
            aug.other_color
        ):
            if all(
                (
                    some_attacker == attacker,
                    attacked in chess.SquareSet.between(attacker, new_attacked),
                    without_attacked.piece_value_at(new_attacked)
                    > aug.piece_value_at(attacked),
                )
            ):
                triples.append((attacker, attacked, new_attacked))

    for a, b, c in triples:
        # TODO: consider removing this condition and handling it another way since pawns can be also pinned
        if aug.piece_type_at(b) == chess.PAWN:
            continue

        # absolute pin
        if aug.piece_type_at(c) == chess.KING:
            return True

        # relative pin
        without_attacked = AugBoard(aug.fen())
        without_attacked.remove_piece_at(b)
        without_attacked.push(chess.Move.null())
        if without_attacked.see(c, attacker=a, moves_without_stop=1) > 0:
            return True

    return False
