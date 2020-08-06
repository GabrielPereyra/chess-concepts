from setuptools import setup
setup(
    name='chess-features',
    entry_points='''
        [console_scripts]
        csv=cli.csv:cli
        features=cli.features:cli
        boards=cli.boards:cli
        plot=cli.plot:cli
    ''',
)
