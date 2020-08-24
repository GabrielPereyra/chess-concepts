import chess

from board import AugBoard


def is_fork_simplest(fen, move):
    aug = AugBoard(fen)
    return (
        not aug.gives_checkmate(move)
        and len(
            aug.move_attacks(move, min_value=aug.piece_value_at(move.from_square) + 1)
        )
        >= 2
        and not aug.can_move_be_captured(move)
    )


def is_fork_simple(fen: str, move: chess.Move) -> bool:
    aug = AugBoard(fen)
    return (
        not aug.gives_checkmate(move)
        and len(
            aug.move_attacks(move, min_value=aug.piece_value_at(move.from_square) + 1)
            | aug.move_attacks(move, min_value=3, defended=False)
        )
        >= 2
        and not aug.can_move_be_captured(move)
    )


def is_fork_see(fen, move):
    aug = AugBoard(fen)
    if aug.gives_checkmate(move):
        return False

    attacked = aug.move_attacks(
        move, min_value=aug.piece_value_at(move.from_square) + 1
    ) | aug.move_attacks(move, min_value=3, defended=False)

    if len(attacked) < 2:
        return False

    aug.push(move)
    return (
        not aug.square_capturers(move.to_square)
        or aug.see(move.to_square, moves_without_stop=1) < 0
    )
