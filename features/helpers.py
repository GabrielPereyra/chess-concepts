from functools import reduce

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


def is_higher_value(a, b):
    return PIECE_TYPE_VALUE[a] > PIECE_TYPE_VALUE[b]


def get_attacking_higher_value_piece(board: chess.Board, color: bool) -> set:
    attacking_higher_values = set()
    for square in chess.SQUARES:
        attacked_piece = board.piece_at(square)
        if attacked_piece is None or attacked_piece.color == color:
            continue
        for attacker_sq in board.attackers(color, square):
            attacker_piece = board.piece_at(attacker_sq)
            if is_higher_value(attacked_piece.piece_type, attacker_piece.piece_type):
                attacking_higher_values.add((attacker_sq, square))
    return attacking_higher_values


def get_attacking_undefended_piece(board: chess.Board, color: bool) -> set:
    attacking_undefended = set()
    for square in chess.SQUARES:
        attacked_piece = board.piece_at(square)
        if attacked_piece is None or attacked_piece.color == color:
            continue
        is_defended = board.is_attacked_by(not color, square)
        if is_defended:
            continue
        attacking_undefended.update(
            (attacker, square) for attacker in board.attackers(color, square)
        )
    return attacking_undefended


if __name__ == "__main__":
    fen = "r1b1kbnr/pp3ppp/4p3/3pP3/3q4/3B4/PP3PPP/RNBQK2R w KQkq - 0 1"
    board = chess.Board(fen)

    before = get_attacking_higher_value_piece(board, chess.WHITE)
    before.update(get_attacking_undefended_piece(board, chess.WHITE))
    print(before)

    move = chess.Move.from_uci("d3b5")
    board.push(move)

    print("###")

    after = get_attacking_higher_value_piece(board, chess.WHITE)
    after.update(get_attacking_undefended_piece(board, chess.WHITE))
    try:
        after.remove(move.to_square)
    except KeyError:
        pass
    print(after)
