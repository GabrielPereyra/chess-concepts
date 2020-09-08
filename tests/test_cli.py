import cli
from click.testing import CliRunner

runner = CliRunner()


def test_csv():
    result = runner.invoke(cli.csv, ["test", "Board", "Stockfish10", "BestMove"])
    assert result.exit_code == 0
