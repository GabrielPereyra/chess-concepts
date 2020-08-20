import chess

from features.abstract import Features


class BitBoards(Features):
    pieces_list = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
    pieces_value = [0.1, 0.3, 0.3, 0.4, 0.9, 10, -0.1, -0.3, -0.3, -0.4, -0.9, -10]

    def __init__(self, fen):
        self.board = chess.Board(fen)

    def features(self):
        sparse_board = {}
        for rank in range(8):
            for file in range(8):
                piece = str(self.board.piece_at(rank * 8 + file))
                if piece in self.pieces_list:
                    piece_ind = self.pieces_list.index(piece)
                    sparse_board[f"{rank}_{file}_{piece}"] = 1
        return sparse_board
