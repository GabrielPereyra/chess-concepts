import utils
import chess
import chess.svg
import pandas as pd
import ipywidgets as widgets
from IPython.core.display import HTML
from ipywidgets import interact, fixed


def fen_to_svg(fen, move):
    board = chess.Board(fen)
    move = chess.Move.from_uci(move)
    arrows = [chess.svg.Arrow(move.from_square, move.to_square)]
    return chess.svg.board(
        board,
        arrows=arrows,
        size=180,
        coordinates=False,
        flipped=board.turn == chess.BLACK,
        style='svg {padding: 0px 10px 5px 0px;}'
    )


def df_to_boards(df):
    html = []
    for fen, move in zip(df['fen'], df['move']):
        html.append(fen_to_svg(fen, move))
    return ''.join(html)


def df_to_table(df, columns=[]):
    df = df.copy()
    df['svg'] = df.apply(lambda row: fen_to_svg(row['fen'], row['move']), axis=1)
    df = df[['svg'] + columns]
    return df.to_html(escape=False, index=False)


def int_range_slider(df, column):
    min = df[column].min()
    max = df[column].max()

    if abs(min) > 1000 or abs(max) > 1000:
        step = 100
        min = int(min / 100) * 100
        max = int(max / 100) * 100

    return widgets.IntRangeSlider(
        value=[min, max],
        min=min,
        max=max,
        step=1,
        description=column,
        continuous_update=False,
        style={'description_width': 'initial'}
    )


def boards_widget_output(df, **kwargs):

    for column, value in kwargs.items():
        min, max = value
        df = df[df[column] >= min]
        df = df[df[column] <= max]

    html = df_to_boards(df[:15])
    return HTML(html)


def boards_widget_controls(df, columns):
    return {column: int_range_slider(df, column) for column in columns}


def init(df, columns):
    interact(
        boards_widget_output,
        df=fixed(df),
        **boards_widget_controls(df, columns)
    )
