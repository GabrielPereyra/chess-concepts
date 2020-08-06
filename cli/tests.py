from click.testing import CliRunner
runner = CliRunner()


def test_lichess_csv():
    from cli.csv import cli
    result = runner.invoke(cli, ['lichess', '0', '0'])
    assert result.exit_code == 0
    assert result.output == 'wrote shard 0\n'


def test_feature_csv():
    from cli.csv import cli
    result = runner.invoke(cli, ['feature', '0', '0', 'Board'])
    assert result.exit_code == 0
    assert result.output == 'wrote shard 0\n'
