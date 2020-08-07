from click.testing import CliRunner

runner = CliRunner()


# TODO: parametrize this to take list of command args.
def test_csv():
    from cli.csv import cli

    result = runner.invoke(cli, ["lichess", "0", "0"])
    assert result.exit_code == 0
    assert result.output == "wrote shard 0\n"

    for feature in ["Board", "PieceCount", "Stockfish10"]:
        result = runner.invoke(cli, ["feature", "0", "0", feature])
        assert result.exit_code == 0
        assert result.output == "wrote shard 0\n"


def test_features():
    from cli.features import cli

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0


def test_boards():
    from cli.boards import cli

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0


def test_plot():
    from cli.plot import cli

    result = runner.invoke(cli, ["hist", "0", "0", "1", "elo", "--testing"])
    assert result.exit_code == 0


def test_model():
    from cli.model import cli
    result = runner.invoke(cli, ["sklearn", "0", "0", "is_blunder"])
    assert result.exit_code == 0
