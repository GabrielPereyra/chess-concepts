import utils
import click
import chess
import features
import pandas as pd


@click.group()
def cli():
    pass


# TODO: add year, month args.
@cli.command()
@click.argument('queries', nargs=-1)
@click.option('csvs', '--csv', multiple=True, default=['lichess'], help='Csvs to load.')
@click.option('--limit', default=3, help='Number of boards to print.')
def list(queries, csvs, limit):
    """
    Print boards that match criteria defined by queries.

    See pandas.DataFrame.query for specifications.

    Examples
    --------
    boards list 'fullmove_number > 5' 'elo < 1200' --csv lichess --csv board
    """

    df = utils.get_df(csvs)
    for query in queries:
        df = df.query(query)
    df = df[:limit]

    print(df)

    for fen in df['fen']:
        print(chess.Board(fen))
        print()


if __name__ == '__main__':
    cli()
