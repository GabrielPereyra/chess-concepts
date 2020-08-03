from setuptools import setup
setup(
    name='chess-features',
    entry_points='''
        [console_scripts]
        cli=cli:cli
    ''',
)
