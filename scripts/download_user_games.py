import requests


username = 'DrDrunkenstein'


url = 'https://lichess.org/api/games/user/{}?analysed=1&evals=1&clocks=1&opening=1'.format(username)


r = requests.get(url)


with open('pgns/{}.pgn'.format(username.lower()), 'w') as f:
    f.write(r.text)
