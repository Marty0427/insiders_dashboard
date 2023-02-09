from dash import Dash, html, dcc, Input, Output

import pandas as pd

app = Dash(__name__)

#df = pd.read_csv('../data/wheels.csv')

app.layout = html.Div([
    dcc.RadioItems(
        id='wheels',
        options=[1, 2, 3],
        value=1
    ),
    html.Div(id='wheels-output'),

    html.Hr(),  # add a horizontal rule
    dcc.RadioItems(
        id='colors',
        options=['red', 'green', 'blue'],
        value='blue'
    ),
    html.Div(id='colors-output')
], style={'fontFamily':'helvetica', 'fontSize':18})

@app.callback(
    Output('wheels-output', 'children'),
    [Input('wheels', 'value')])
def callback_a(wheels_value):
    return 'You\'ve selected "{}"'.format(wheels_value)

@app.callback(
    Output('colors-output', 'children'),
    [Input('colors', 'value')])
def callback_b(colors_value):
    return 'You\'ve selected "{}"'.format(colors_value)

if __name__ == '__main__':
    server = app.server
    app.run_server()
