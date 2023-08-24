from dash import Dash, html, dcc, dash_table, callback, Input, Output
import pairs
import reg
import plotly.express as px




df = pairs.get_df()
## app
app = Dash(__name__)

#fig, tab = None, None

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Pairs Trading', children=[
            html.H1("Pairs Trading"),
            html.Label("Lookback Period:"),
            dcc.Slider(
                id="lookback-slider",
                min=5,
                max=50,
                step=5,
                value=20,
                marks={i: str(i) for i in range(5, 51, 5)}
            ),
            html.Label('Entry Threshold:'),
            dcc.Input(id = "entry", value=1.0, type='number'),
            html.Label('Exit Threshold:'),
            dcc.Input(id = "exit",  value=0.2, type='number'),
            html.Label("Stocks:"),
            dcc.Dropdown(
                id="stock-dropdown1",
                options=[{"label": stock_name1, "value": stock_name1} for stock_name1 in ["AAPL","MSFT","TSLA"]],
                value="AAPL"
            ),
            dcc.Dropdown(
                id="stock-dropdown2",
                options=[{"label": stock_name2, "value": stock_name2} for stock_name2 in ["AAPL", "MSFT", "TSLA"]],
                value="MSFT"
            ),
            html.Label("Metrics:"),
            html.Table([
                html.Tr([html.Td("sharpe"), html.Td(id='sharpe')]),
                html.Tr([html.Td("sortino"), html.Td(id='sortino')]),
            ]),
            html.Label("Portfolio Performance:"),
            dcc.Graph(id="portfolio-graph")
        ]),
        dcc.Tab(label='Index Regression', children=[
            html.H1("Index Regression"),
            html.Label("Index:"),
            dcc.Dropdown(
                id="index-dropdown",
                options=[{"label": ind_name, "value": ind_name} for ind_name in ["sp500","nasdaq100","russel2000"]],
                value="nasdaq100"
            ),
            html.Label('Start Date:'),
            dcc.Input(id = "start-date",  value="2023-01-10", type='text'),
            html.Label('End Date:\n'),
            dcc.Input(id = "end-date",  value="2023-08-01", type='text'),
            html.Br(),
            html.Label("Most Explanatory Subset:"),
            html.Table(id='subset'),
            html.Label('Stock 1:'),
            dcc.Input(id = "col1",  value="AAPL", type='text'),
            html.Label('Stock 2:'),
            dcc.Input(id = "col2",  value="MSFT", type='text'),
            html.Label('Stock 3:\n'),
            dcc.Input(id = "col3",  value="TSLA", type='text'),
            html.Br(),
            html.Label("Scatter Plot:"),
            dcc.Graph(id="reg-graph"),
            html.Label("Regression Summary:"),
            html.Div(id='reg-summary')
            ]),
        ])
    ])
#])

@app.callback(
    Output("portfolio-graph", "figure"),
    Output("sharpe", "children"),
    Output("sortino", "children"),
    Input("stock-dropdown1", "value"),
    Input("stock-dropdown2", "value"),
    Input("lookback-slider", "value"),
    Input("entry", "value"),
    Input("exit", "value")
)
def update_graph(stock1, stock2, lookback_period, entry, exit):
    # Apply the pairs trading strategy

    trade_out = pairs.trade(df[stock1], df[stock2], capital=1.0,
                            lookback_period=lookback_period, entry_threshold=entry, exit_threshold=exit)

    # Create a plot of portfolio value
    figure = px.line(trade_out["value"])
    return figure, trade_out["sharpe"], trade_out["sortino"]

#fig, tab = update_graph(stock1, stock2, lookback_period)

@app.callback(
    Output("reg-summary", "children"),
    Output("reg-graph", "figure"),
    Output("subset", "children"),
    Input("col1", "value"),
    Input("col2", "value"),
    Input("col3", "value"),
    Input("index-dropdown", "value"),
    Input("start-date", "value"),
    Input("end-date", "value")
)
def update_reg(col1, col2, col3, index, start_date, end_date):
    summ, y, fitted = reg.regression([col1, col2, col3], index, start_date, end_date)
    subset = reg.subset(index, 10, start_date, end_date)
    return print(summ), px.scatter(y, fitted), dash_table.DataTable(subset.to_dict("pc"))

if __name__ == "__main__":
    app.run_server(debug=True)