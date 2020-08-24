from typing import Optional, Set, Tuple

import chess

from board import AugBoard


def get_mating_net(fen) -> Optional[Tuple[chess.SquareSet, chess.SquareSet]]:
    aug = AugBoard(fen)
    if not aug.is_checkmate():
        return None

    their_king = aug.current_color_king()
    maters = aug.attackers(aug.other_color, their_king)

    escape_squares = [
        square for square in aug.attacks(their_king) if aug.piece_at(square) is None
    ]
    cutters = chess.SquareSet()
    for escape_square in escape_squares:
        cutters.update(aug.attackers(aug.other_color, escape_square))
    return maters, cutters


def get_move_mating_net_piece_types(
    fen: str, move: chess.Move
) -> Optional[Tuple[Set[chess.PieceType], Set[chess.PieceType]]]:
    aug = AugBoard(fen)
    aug.push(move)
    return get_mating_net_piece_types(aug.fen())


def get_mating_net_piece_types(
    fen: str,
) -> Optional[Tuple[Set[chess.PieceType], Set[chess.PieceType]]]:
    mating_net = get_mating_net(fen)
    if mating_net is None:
        return None
    maters, cutters = mating_net
    aug = AugBoard(fen)
    return (
        {aug.piece_type_at(square) for square in maters},
        {aug.piece_type_at(square) for square in cutters},
    )
