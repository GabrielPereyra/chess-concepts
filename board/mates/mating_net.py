from typing import Optional, Set, Tuple, Counter as CounterType
from collections import Counter

import chess

import board


def get_mating_net(fen) -> Optional[Tuple[chess.SquareSet, chess.SquareSet]]:
    aug = board.AugBoard(fen)
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
    cutters -= maters
    return maters, cutters


def get_mating_net_piece_type_counters(fen: str) -> Optional[Tuple[Counter, Counter]]:
    mating_net = get_mating_net(fen)

    if mating_net is None:
        return None

    maters, cutters = mating_net
    aug = board.AugBoard(fen)
    return (
        Counter(aug.piece_type_at(square) for square in maters),
        Counter(aug.piece_type_at(square) for square in cutters),
    )


def get_move_mating_net_piece_type_counters(
    fen: str, move: chess.Move
) -> Optional[Tuple[Set[chess.PieceType], Set[chess.PieceType]]]:
    aug = board.AugBoard(fen)
    aug.push(move)
    return get_mating_net_piece_type_counters(aug.fen())


def is_mate_with_pieces(
    fen: str, move: chess.Move, expected_pieces: CounterType[chess.PieceType]
) -> bool:
    try:
        maters, cutters = get_move_mating_net_piece_type_counters(fen, move)
    except TypeError:
        return False
    return maters + cutters == expected_pieces
