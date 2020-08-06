from click.testing import CliRunner
runner = CliRunner()


def test_csv():
    from cli.csv import cli

    result = runner.invoke(cli, ['lichess', '0', '0'])
    assert result.exit_code == 0
    assert result.output == 'wrote shard 0\n'

    result = runner.invoke(cli, ['feature', '0', '0', 'Board'])
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
