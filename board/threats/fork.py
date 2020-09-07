import chess

import board


def creates_fork_threat(fen: str, move: chess.Move) -> bool:
    aug = board.AugBoard(fen)

    # TODO: do we want to exclude checks?
    if aug.gives_check(move):
        return False

    aug.push(move)
    aug.push(chess.Move.null())
    return any(
        board.Tactic.FORK in aug.move_tactics(next_move)
        for next_move in aug.legal_moves
    )
