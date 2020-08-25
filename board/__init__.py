from typing import Optional, Set, Tuple, Iterator, Dict, List

from board.tactics import Tactic
from board.threats import Threat

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


class AugBoard:
    def __init__(self, fen: str):
        self._board = chess.Board(fen)

    @classmethod
    def from_board(cls, board: chess.Board):
        return cls(board.fen())

    def copy(self):
        return self.from_board(self._board)

    @property
    def current_color(self) -> bool:
        return self._board.turn

    @property
    def other_color(self) -> bool:
        return not self.current_color

    def piece_at(self, square: int) -> Optional[chess.Piece]:
        return self._board.piece_at(square)

    def piece_value_at(self, square: int) -> int:
        return PIECE_TYPE_VALUE[self._board.piece_type_at(square)]

    def piece_color_at(self, square: int) -> Optional[chess.Color]:
        piece = self._board.piece_at(square)
        if piece is None:
            return None
        return piece.color

    def piece_type_at(self, square: int) -> Optional[chess.PieceType]:
        return self._board.piece_type_at(square)

    def current_color_king(self) -> Optional[chess.Square]:
        return self._board.king(self.current_color)

    def other_color_king(self) -> Optional[chess.Square]:
        return self._board.king(self.other_color)

    def remove_piece_at(self, square: chess.Square) -> Optional[chess.Piece]:
        return self._board.remove_piece_at(square)

    def is_checkmate(self) -> bool:
        return self._board.is_checkmate()

    def is_en_passant(self, move: chess.Move) -> bool:
        return self._board.is_en_passant(move)

    def is_capture(self, move: chess.Move) -> bool:
        return self._board.is_capture(move)

    def is_check(self) -> bool:
        return self._board.is_check()

    def fen(self) -> str:
        return self._board.fen()

    def push(self, move: chess.Move) -> None:
        return self._board.push(move)

    def pop(self) -> chess.Move:
        return self._board.pop()

    def peek(self) -> chess.Move:
        return self._board.peek()

    def occupied_by(self, color: chess.Color) -> chess.SquareSet:
        return chess.SquareSet(self._board.occupied_co[color])

    def attacks(self, square: int) -> chess.SquareSet:
        return self._board.attacks(square)

    def attackers(self, color: chess.Color, square: int) -> chess.SquareSet:
        return self._board.attackers(color, square)

    def attackers_mask(
        self, color: chess.Color, square: chess.Square
    ) -> chess.Bitboard:
        return self._board.attackers_mask(color, square)

    def count_material(self, color: bool) -> int:
        return sum(
            PIECE_TYPE_VALUE[piece_type] * len(self._board.pieces(piece_type, color))
            for piece_type in chess.PIECE_TYPES
        )

    def absolute_material_balance(self) -> int:
        return self.count_material(chess.WHITE) - self.count_material(chess.BLACK)

    def relative_material_balance(self) -> int:
        return self.count_material(self.current_color) - self.count_material(
            self.other_color
        )

    def generate_legal_moves_from_square(self, square: int) -> Iterator[chess.Move]:
        return self._board.generate_legal_moves(from_mask=chess.BB_SQUARES[square])

    def has_mate(self):
        return any(
            self.gives_checkmate(move) for move in self._board.generate_legal_moves()
        )

    def has_hanging_piece_capture(self):
        return any(
            not self.is_square_defended(move.to_square)
            for move in self._board.generate_legal_captures()
        )

    def has_positive_see_capture(self):
        return any(
            self.see(move.to_square, move.from_square) > 0
            for move in self._board.generate_legal_captures()
        )

    def see(
        self,
        square: int,
        attacker: Optional[int] = None,
        moves_without_stop: int = 0,
        move_num: int = 1,
    ) -> int:
        """
        Does Static Exchange Evaluation (SEE): https://www.chessprogramming.org/Static_Exchange_Evaluation
        Has additional options:
        - specify first attacker
        - specify the number of first moves without option to stop the sequence
        """
        value = 0
        if attacker is None:
            try:
                attacker = min(self.square_capturers(square), key=self.piece_value_at)
            except ValueError:
                pass
        if attacker is not None:
            on_square_value = self.piece_value_at(square)
            self._board.push(chess.Move(attacker, square))
            value = on_square_value - self.see(
                square, moves_without_stop=moves_without_stop, move_num=move_num + 1
            )
            if move_num > moves_without_stop:
                value = max(value, 0)
            self._board.pop()
        return value

    def gives_checkmate(self, move: chess.Move) -> bool:
        """
        Probes if the given move would give checkmate. The move
        must be at least pseudo-legal.
        """
        self._board.push(move)
        try:
            return self._board.is_checkmate()
        finally:
            self._board.pop()

    def gives_check(self, move: chess.Move) -> bool:
        return self._board.gives_check(move)

    def move_capturers(self, move: chess.Move) -> chess.SquareSet:
        self._board.push(move)
        try:
            res = chess.SquareSet()
            for m in self._board.generate_legal_captures(
                to_mask=chess.BB_SQUARES[move.to_square]
            ):
                res.add(m.from_square)
            return res
        finally:
            self._board.pop()

    def square_capturers(self, square: int) -> chess.SquareSet:
        """
        Returns a set of squares that can perform a legal capture on the given square in the current position.
        """
        res = chess.SquareSet()
        for m in self._board.generate_legal_captures(to_mask=chess.BB_SQUARES[square]):
            res.add(m.from_square)
        return res

    def can_move_be_captured(self, move: chess.Move) -> bool:
        self._board.push(move)
        try:
            return bool(self.square_capturers(move.to_square))
        finally:
            self._board.pop()

    def is_square_defended(self, square: int) -> bool:
        return (
            self._board.attackers_mask(self.piece_color_at(square), square)
            != chess.BB_EMPTY
        )

    def is_attacked_by(self, color: chess.Color, square: chess.Square) -> bool:
        return self._board.is_attacked_by(color, square)

    def move_attacks(
        self,
        move: chess.Move,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        defended: Optional[bool] = None,
    ) -> chess.SquareSet:
        self._board.push(move)
        try:
            squares = chess.SquareSet(
                self._board.attacks_mask(move.to_square)
                & self._board.occupied_co[self.current_color]
            )

            res = chess.SquareSet()
            for square in squares:
                if (
                    (min_value is None or self.piece_value_at(square) >= min_value)
                    and (max_value is None or self.piece_value_at(square) <= max_value)
                    and (
                        defended is None or self.is_square_defended(square) == defended
                    )
                ):
                    res.add(square)
            return res
        finally:
            self._board.pop()

    def attacking_pairs(
        self, color: chess.Color
    ) -> Set[Tuple[chess.Square, chess.Square]]:
        """
        Returns a set of square pairs (attacker, attacked) for the color whose move it is.
        """
        res = set()
        for square in chess.SQUARES:
            attacked_piece = self._board.piece_at(square)
            if attacked_piece is None or attacked_piece.color == color:
                continue
            res.update(
                (attacker, square) for attacker in self._board.attackers(color, square)
            )
        return res

    def attacks_mask(self, square: chess.Square) -> chess.Bitboard:
        return self._board.attacks_mask(square)

    def occupied_co(self, color: chess.Color) -> chess.Bitboard:
        return self._board.occupied_co[color]

    def _pv_contains(self, pv: List[chess.Move], detectors: Dict, none_value) -> List:
        detected = set()
        aug = AugBoard(self.fen())
        for i in range(0, len(pv), 2):
            our_move = pv[i]
            detected.update(
                value
                for value, detector in detectors.items()
                if detector(aug.fen(), our_move)
            )
            aug.push(our_move)
            if i + 1 < len(pv):
                their_move = pv[i + 1]
                aug.push(their_move)
        return sorted(detected) if detected else [none_value]

    def pv_tactics(self, pv: List[chess.Move]) -> List[Tactic]:
        return self._pv_contains(pv, Tactic.detectors(), Tactic.NONE)

    def move_tactics(self, move: chess.Move) -> List[Tactic]:
        return self.pv_tactics(pv=[move])

    def pv_threats(self, pv: List[chess.Move]) -> List[Threat]:
        return self._pv_contains(pv, Threat.detectors(), Threat.NONE)

    def move_threats(self, move: chess.Move) -> List[Threat]:
        return self.pv_threats(pv=[move])


if __name__ == "__main__":
    fen = "r5k1/1p1q1pbp/6p1/2Pp4/p3nQ2/P4P2/B2B2PP/2R4K b - - 0 1"
    pv = ["e4f2", "h1g1", "f2d3", "f4e3", "d3c1"]
    pv = [chess.Move.from_uci(move_uci) for move_uci in pv]
    aug = AugBoard(fen)
    print(aug.pv_tactics(pv))
    print(aug.move_tactics(pv[0]))
