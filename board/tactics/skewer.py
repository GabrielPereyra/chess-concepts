import chess

import board


def is_skewer_see(fen: str, move: chess.Move) -> bool:
    aug = board.AugBoard(fen)

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

        if not any(True for _ in aug.generate_legal_moves_from_square(attacked)):
            continue

        if aug.piece_value_at(attacker) > aug.piece_value_at(attacked):
            continue

        if (
            aug.square_capturers(attacker)
            and aug.see(attacker, moves_without_stop=1) >= 0
        ):
            continue

        without_attacked = board.AugBoard(aug.fen())
        without_attacked.remove_piece_at(attacked)

        for some_attacker, new_attacked in without_attacked.attacking_pairs(
            aug.other_color
        ):
            if aug.piece_value_at(new_attacked) < 3:
                continue

            if all(
                (
                    some_attacker == attacker,
                    attacked in chess.SquareSet.between(attacker, new_attacked),
                    without_attacked.piece_value_at(new_attacked)
                    < aug.piece_value_at(attacked),
                )
            ):
                triples.append((attacker, attacked, new_attacked))

    for a, b, c in triples:
        found_escape = False

        for m in aug.generate_legal_moves_from_square(b):
            m_val = aug.piece_value_at(m.to_square)
            try:
                aug.push(m)
                if m_val - aug.see(c, attacker=a) >= 0:
                    found_escape = True
                    break
            finally:
                aug.pop()

        if not found_escape:
            return True

    return False
