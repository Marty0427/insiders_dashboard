import dash
from dash import html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
from base import insiders
import datetime as dt


def get_data(trades_len = 10, period = 'mo2', ratio = 80, summary = pd.read_pickle('summary_R3000.pkl').round(3), offset = 100):
    
    today = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if today.weekday() == 6:
        date = today - dt.timedelta(days = 2 + offset)
    elif today.weekday() == 5:
        date = today - dt.timedelta(days = 1 + offset)
    else:
        date = today - dt.timedelta(days = offset)

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



def make_app():
    app = dash.Dash(__name__)
    df = get_data()

    table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
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
        html.Div(id='not', style = {'display': 'none'}),
        table
    ])

    @app.callback(
    Output(component_id='table', component_property='data'),
    [Input(component_id='upgrade-table-button', component_property='n_clicks')])
    def upgrade_table(n_clicks):
        if n_clicks > 0:
            df = get_data(trades_len = 10, period = 'mo2', ratio = 80)
            return df.to_dict('records')
        
    @app.callback(
    Output(component_id='not', component_property='children'),
    [Input(component_id='export-table-button', component_property='n_clicks'),
     State(component_id='table', component_property='selected_rows')])
    def export_table(n_clicks, rows):
        if n_clicks > 0:
            #df = get_data(trades_len = 10, period = 'mo2', ratio = 80)
            df.iloc[rows].to_csv(f'daily/df_selected_{dt.date.today()}.csv')
            #return df.to_dict('records')
        
    return app

if __name__ == '__main__':
    app = make_app()
    app.run_server(debug=False)
