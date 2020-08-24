import chess

from board import AugBoard


def is_discovered_attack_simple(fen, move):
    aug = AugBoard(fen)

    attackers_before_move = aug.attacking_pairs(aug.current_color)
    aug.push(move)
    attackers_after_move = aug.attacking_pairs(aug.other_color)

    for attacker, attacked in attackers_after_move - attackers_before_move:
        if any(
            (
                attacker == move.to_square,
                move.from_square not in chess.SquareSet.between(attacker, attacked),
            )
        ):
            continue

        if aug.piece_value_at(attacker) < aug.piece_value_at(attacked):
            return True

    return False


def is_discovered_attack_see(fen, move):
    aug = AugBoard(fen)

    attackers_before_move = aug.attacking_pairs(aug.current_color)
    aug.push(move)
    attackers_after_move = aug.attacking_pairs(aug.other_color)

    for attacker, attacked in attackers_after_move - attackers_before_move:
        if any(
            (
                attacker == move.to_square,
                move.from_square not in chess.SquareSet.between(attacker, attacked),
                aug.is_checkmate() and aug.piece_type_at(attacked) != chess.KING,
            )
        ):
            continue

        if all(
            (
                aug.piece_value_at(attacker) < aug.piece_value_at(attacked)
                or not aug.is_square_defended(attacked),
                attacked not in aug.square_capturers(move.to_square),
                (
                    not aug.square_capturers(attacker)
                    or aug.see(attacker, moves_without_stop=1) < 0
                ),
            )
        ):
            return True

    return False
