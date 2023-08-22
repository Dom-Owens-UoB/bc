from dash import Dash, html, dcc, dash_table, callback, Input, Output
import pairs

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Pairs Trading"),
    dash_table.DataTable(id="portfolio-table", page_size=10),
    dcc.Graph(id="portfolio-graph"),
    html.Label("Lookback Period:"),
    dcc.Slider(
        id="lookback-slider",
        min=5,
        max=50,
        step=5,
        value=20,
        marks={i: str(i) for i in range(5, 51, 5)}
    ),
    dcc.Dropdown(
        id="stock-dropdown1",
        options=[{"label": stock_name1, "value": stock_name1} for stock_name1 in ["AAPL","MSFT","TSLA"]],
        value="AAPL"
    ),
    dcc.Dropdown(
        id="stock-dropdown2",
        options=[{"label": stock_name2, "value": stock_name2} for stock_name2 in ["AAPL", "MSFT", "TSLA"]],
        value="MSFT"
    )
])

@app.callback(
    Output("portfolio-graph", "figure"),
    Input("lookback-slider", "value"),
    Input("stock-dropdown1", "value"),
    Input("stock-dropdown2", "value")
)
def update_graph(stock1, stock2, lookback_period):
    # Apply the pairs trading strategy
    trade_out = pairs.trade(stock1, stock2, capital=1.0,
                            lookback_period=lookback_period, entry_threshold=1.0, exit_threshold=0.2)

    # Create a plot of portfolio value
    figure = {
        "data": [
            {"x": stock1.index, "y": trade_out["portfolio_value"], "type": "line", "name": "Portfolio Value"},
            {"x": stock1.index, "y": stock1, "type": "line", "name": "Stock 1 Price"},
            {"x": stock2.index, "y": stock2, "type": "line", "name": "Stock 2 Price"}
        ],
        "layout": {"title": "Pairs Trading"}
    }

    table = dash_table.DataTable([trade_out["sharpe"], trade_out["sortino"]])


    return figure, table


if __name__ == "__main__":
    app.run_server(debug=True)