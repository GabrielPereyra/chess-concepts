import plotly.express as px


@csv.command()
@click.argument('feature')
@click.option('--elo_bin', default=200)
def plot(feature, elo_bin):
    """
    Create a plotly plot of feature vs. accuracy by elo. Assumes you have created csvs/data.csv and the feature exists as a column.
    """

    df = pd.read_csv('csvs/data.csv')

    # TODO: generalize this to remove feature values with low counts.
    if feature == 'best_mate':
        df = df[df[feature] < 10]

    df = df[df['elo'] > 800]
    df = df[df['elo'] < 2200]


    df['elo'] = df['elo'].apply(lambda elo: int(elo / elo_bin) * elo_bin)
    df = df.groupby([feature, 'elo'], as_index=False).mean()

    fig = px.line(
        df,
        x='elo',
        y='correct',
        color=feature
    )

    fig.show()
