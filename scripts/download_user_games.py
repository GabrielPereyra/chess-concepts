import lichess.api
from lichess.format import SINGLE_PGN


username = 'pawn_f_kennedy'


pgn = lichess.api.user_games(
    username,
    format=SINGLE_PGN,
    clocks=True,
    evals=True,
    opening=True,
    # auth='API TOKEN'
)


with open('pgns/{}.pgn'.format(username), 'w') as f:
    f.write(pgn)
