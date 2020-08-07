import utils
import click
import plotly.express as px


@click.group()
def cli():
    pass


# TODO: add option for shards...
@cli.command()
@click.argument('year')
@click.argument('month')
@click.argument('shards', type=int) # option to use all (set to None if -1?)
@click.argument('x')
@click.argument('queries', nargs=-1)
@click.option('csvs', '--csv', multiple=True, default=['lichess'], help='Csvs to load.')
@click.option('--testing', is_flag=True, help='Prevent tab from opening.')
def hist(year, month, shards, x, queries, csvs, testing):
    df = utils.get_df(csvs, years=[year], months=[month], shards=range(shards))
    fig = px.histogram(df, x=x)
    if testing:
        return
    else:
        fig.show()
