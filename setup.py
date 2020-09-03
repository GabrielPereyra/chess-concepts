from setuptools import setup

setup(
    name="chess-features",
    entry_points="""
        [console_scripts]
        csv=cli.csv:cli
        features=cli.features:cli
        boards=cli.boards:cli
        model=cli.model:cli
    """,
)
