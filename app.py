import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import pymongo
from datetime import datetime
from datetime import timezone
from datetime import timedelta

import colorlover as cl

colorscale = cl.scales['9']['qual']['Paired']

app = dash.Dash(
    __name__, 
    assets_external_scripts='https://cdn.plot.ly/plotly-finance-1.28.0.min.js'
)
server = app.server

app.scripts.config.serve_locally = False

#function to get stockPrice and return dataframe
def getPrices(collection, symbol):
    query = [
        {"$match":{"Ticker":symbol}}
    ]

    cursor = collection.aggregate(query)
    df = pd.DataFrame(list(cursor))
    df.drop_duplicates(['Ticker'])
    df.set_index('Ticker', inplace = True)

    return df

#connect  to database
client = pymongo.MongoClient()
db = client.Invest
collection_price = db['DailyPrice']

#get distinct ticker
tickers = collection_price.distinct('Ticker')
tickers.sort()
#print(tickers)

app.layout = html.Div([
    html.Div([
        html.H2('Dashboard',
                style={'display': 'inline',
                       'float': 'left',
                       'font-size': '2.65em',
                       'margin-left': '7px',
                       'font-weight': 'bolder',
                       'font-family': 'Product Sans',
                       'color': "rgba(117, 117, 117, 0.95)",
                       'margin-top': '20px',
                       'margin-bottom': '0'
                       })
    ]),
    dcc.Dropdown(
        id='stock-ticker-input',
        options=[{'label': s[0], 'value': str(s[1])}for s in zip(tickers, tickers)],
        value=[],
        multi=True
    ),
    html.Div(id='graphs')
], className="container")

@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_graph(tickers):
    graphs = []

    if not tickers:
        graphs.append(html.H3(
            "Select a stock ticker.",
            style={'marginTop': 20, 'marginBottom': 20}
        ))
    else:
        for i, ticker in enumerate(tickers):
            dff = getPrices(collection_price, ticker)

            candlestick = {
                'x': dff['date'],
                'open': dff['open'],
                'high': dff['high'],
                'low': dff['low'],
                'close': dff['close'],
                'type': 'candlestick',
                'name': ticker,
                'legendgroup': ticker,
                'increasing': {'line': {'color': colorscale[0]}},
                'decreasing': {'line': {'color': colorscale[1]}},
                'yaxis' : 'y2'
            }

            Bar = {
                'x': dff['date'],
                'y': dff['volume'],
                'type':'bar',
                'name':ticker + ' volume'
            }
            
            graphs.append(dcc.Graph(
                id=ticker,
                figure={
                    'data': [candlestick] + [Bar],
                    'layout': {
                        'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
                        'legend': {'x': 0},
                        'yaxis' : {'domain' : [0, 0.2]},
                        'yaxis2' : {'domain':[0.2,0.8]}
                    }
                }
            ))


    return graphs

if __name__ == '__main__':
    app.run_server(debug=True)