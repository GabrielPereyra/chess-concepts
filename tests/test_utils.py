import utils
from cli.csv import cli
from click.testing import CliRunner


# create csvs.
runner = CliRunner()
runner.invoke(cli, ['lichess', '0', '0'])
runner.invoke(cli, ['feature', '0', '0', 'Board'])


# TODO: add remaining features.
def test_get_type_df():
    types = ['lichess', 'board']
    for type in types:
        df = utils.get_type_df(type)
        assert len(df) == 39


def test_get_df():
    df = utils.get_df(['lichess', 'board'])
    assert len(df) == 39
