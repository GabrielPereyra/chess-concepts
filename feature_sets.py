import features

base = ['elo', 'best_mate', 'best_score2']
board = features.Board.feature_names()
piece_count = features.PieceCount.feature_names()
best_move = features.BestMove.feature_names()
best_pv = features.BestPV.feature_names()
their_king = features.TheirKing.feature_names()
