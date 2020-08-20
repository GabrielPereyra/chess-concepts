import chess

from features.abstract import Features


class BitBoards(Features):
    pieces_list = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
    pieces_value = [0.1, 0.3, 0.3, 0.4, 0.9, 10, -0.1, -0.3, -0.3, -0.4, -0.9, -10]

    def __init__(self, fen):
        self.board = chess.Board(fen)

    def features(self):
        sparse_board = {}
        for square, piece in self.board.piece_map().items():
            sparse_board[f"{chess.SQUARE_NAMES[square]}_{piece.symbol()}"] = 1
        return sparse_board


if __name__ == '__main__':
    board = chess.Board()
    print(BitBoards(board.fen()).features())
