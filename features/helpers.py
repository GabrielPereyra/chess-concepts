from enum import Enum

import chess

PIECE_TYPE_VALUE = {
    None: 0,
    0: 0,
    1: 1,
    2: 3,
    3: 3,
    4: 5,
    5: 9,
    6: 10,
}


class GamePhase(Enum):
    OPENING = 0
    ENDGAME = 1
    MIDDLEGAME = 2


class PositionOpenness(Enum):
    OPEN = 0
    SEMI_OPEN = 1
    CLOSED = 2


def square_from_name(square_name):
    file, rank = square_name
    return chess.square(ord(file) - ord("a"), int(rank) - 1)


def is_greater_value(a, b):
    return PIECE_TYPE_VALUE[a] > PIECE_TYPE_VALUE[b]


def is_same_value(a, b):
    return PIECE_TYPE_VALUE[a] == PIECE_TYPE_VALUE[b]


def is_lower_value(a, b):
    return PIECE_TYPE_VALUE[a] < PIECE_TYPE_VALUE[b]


def is_greater_equal_value(a, b):
    return not is_lower_value(a, b)


def is_lower_equal_value(a, b):
    return not is_greater_value(a, b)


def get_attacking(
    board: chess.Board,
    color: bool,
    piece_type_filter=None,
    attacker_is_defended=None,
    attacked_is_defended=None,
) -> set:
    res = set()
    for square in chess.SQUARES:
        attacked_piece = board.piece_at(square)
        if attacked_piece is None or attacked_piece.color == color:
            continue

        if attacked_is_defended is not None:
            defended = board.is_attacked_by(not color, square)
            if attacked_is_defended != defended:
                continue

        for attacker_sq in board.attackers(color, square):
            if attacker_is_defended is not None:
                defended = board.is_attacked_by(color, square)
                if attacker_is_defended != defended:
                    continue

            attacker_piece = board.piece_at(attacker_sq)
            if piece_type_filter is None or piece_type_filter(
                attacker_piece.piece_type, attacked_piece.piece_type
            ):
                res.add((attacker_sq, square))
    return res


def count_material(board: chess.Board, color: bool) -> int:
    return sum(
        PIECE_TYPE_VALUE[piece_type] * len(board.pieces(piece_type, color))
        for piece_type in chess.PIECE_TYPES
    )
