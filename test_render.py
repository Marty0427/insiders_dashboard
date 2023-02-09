import dash
import dash_auth
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, State, dash_table

app = dash.Dash(__name__,
                meta_tags=[
                    {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}],
                external_stylesheets=[dbc.themes.QUARTZ])

server = app.server
app.title = 'Title'
app.layout = dbc.Container(fluid=True, children=[])

@app.callback(
    [Output('some_stuff', 'children'),],
    [Input('stuff', 'value')])

def display_something(value):
    return value

if __name__ == '__main__':
    app.run_server(debug=False)
