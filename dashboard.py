from dash import Dash, html, dcc, dash_table, callback, Input, Output
import pairs
import plotly.express as px




df = pairs.get_df()
## app
app = Dash(__name__)

#fig, tab = None, None

app.layout = html.Div([
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
    html.Label('Entry Threshold'),
    dcc.Input(id = "entry", value=1.0, type='number'),
    html.Label('Exit Threshold'),
    dcc.Input(id = "exit",  value=0.2, type='number'),
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
    html.Table([
        html.Tr([html.Td("sharpe"), html.Td(id='sharpe')]),
        html.Tr([html.Td("sortino"), html.Td(id='sortino')]),
    ]),
    dcc.Graph(id="portfolio-graph")
])

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


if __name__ == "__main__":
    app.run_server(debug=True)