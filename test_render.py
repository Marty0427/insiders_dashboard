from dash import Dash, html, dcc, Input, Output
import flask
import pandas as pd

server = flask.Flask(__name__) # define flask app.server

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server) # call flask server


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
    app.run_server()
