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


def count_material(board: chess.Board, color: bool) -> int:
    return sum(
        PIECE_TYPE_VALUE[piece_type] * len(board.pieces(piece_type, color))
        for piece_type in chess.PIECE_TYPES
    )
