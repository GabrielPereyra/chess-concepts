import utils
import click
import plotly.express as px


@click.group()
def cli():
    pass


@cli.command()
@click.argument('x')
@click.argument('queries', nargs=-1)
@click.option('csvs', '--csv', multiple=True, default=['lichess'], help='Csvs to load.')
def hist(x, queries, csvs):
    df = utils.get_df(csvs)
    fig = px.histogram(df, x=x)
    fig.show()


# TODO: add other types of plots.
