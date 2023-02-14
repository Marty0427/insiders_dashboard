from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
from pandas.tseries.offsets import BDay
from base import insiders
import datetime as dt
import flask

server = flask.Flask(__name__) # define flask app.server

app = Dash(__name__,server=server) # call flask server



def get_data(trades_len = 10, period = 'mo2', ratio = 80, summary = pd.read_csv('data/summary_R3000.csv').round(3), offset = 100):
    
    today = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    date = today - BDay(offset)

    df = insiders.fv_last_insiders(side = 'buy')
    df_last = df[df.SEC >= date]
    
    insider_bool = summary.insider.isin(df_last.insider.unique())
    len_bool = summary.len > trades_len
    ratio_bool = summary[f'{period}_ratio'] > ratio

    #
    df_rank = summary[insider_bool & len_bool & ratio_bool].sort_values(f'{period}_per_trade', ascending = False).reset_index()
    df_sliced = df_last[df_last.insider.isin(df_rank.insider)]

    col_list = list(summary.columns[0:2]) + [f'{period}_sum', f'{period}_per_trade', f'{period}_ratio']
    return pd.merge(df_sliced, summary[col_list], on='insider')

df = get_data()

table = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
    editable=True,
    #filter_action="native",
    sort_action="native",
    sort_mode="multi",
    column_selectable="single",
    row_selectable="multi",
    row_deletable=False,
    selected_columns=[],
    selected_rows=[],
    page_action="native",
    page_current= 0,
    page_size= 200,
    style_header={'fontWeight': 'bold'}
)

app.layout = html.Div([
    html.Button(id='upgrade-table-button', children='Upgrade Table', n_clicks=0),
    html.Button(id='export-table-button', children='Export Table', n_clicks=0),
    html.Div([dcc.Slider(
        min=0,
        max=10,
        step=1,
        value=1,
        id = 'offset-slider'
    )]),

    html.Div(id='not', style = {'display': 'none'}),
    table
])

@app.callback(
Output(component_id='table', component_property='data'),
[Input(component_id='upgrade-table-button', component_property='n_clicks'),
 State(component_id='offset-slider', component_property='value')])
def upgrade_table(n_clicks, offset):
    if n_clicks > 0:
        df = get_data(trades_len = 10, period = 'mo2', ratio = 80, offset = offset)
        return df.to_dict('records')
    

@app.callback(
Output(component_id='not', component_property='children'),
[Input(component_id='export-table-button', component_property='n_clicks'),
    State(component_id='table', component_property='selected_rows')])
def export_table(n_clicks, rows):
    if n_clicks > 0:
        df.iloc[rows].to_csv(f'daily/df_selected_{dt.date.today()}.csv')
    

if __name__ == '__main__':
    app.run_server(debug=True)

