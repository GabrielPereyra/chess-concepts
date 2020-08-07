from click.testing import CliRunner
runner = CliRunner()


# TODO: option to use lower case feature name.


def test_csv():
    from cli.csv import cli

    result = runner.invoke(cli, ['lichess', '0', '0'])
    assert result.exit_code == 0
    assert result.output == 'wrote shard 0\n'

    result = runner.invoke(cli, ['feature', '0', '0', 'Board'])
    assert result.exit_code == 0
    assert result.output == 'wrote shard 0\n'

    result = runner.invoke(cli, ['feature', '0', '0', 'Stockfish10'])
    assert result.exit_code == 0
    assert result.output == 'wrote shard 0\n'


def test_features():
    from cli.features import cli
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0


def test_boards():
    from cli.boards import cli

    # TODO: this expects csvs to exists (need to ensure they do.).
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0


# TODO: prevent this from generating plot?
def test_plot():
    from cli.plot import cli
    result = runner.invoke(cli, ['hist', '0', '0', '1', 'elo', '--testing'])
    assert result.exit_code == 0
