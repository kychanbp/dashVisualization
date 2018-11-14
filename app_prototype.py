import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import plotly.graph_objs as go

import pandas as pd
import numpy as np
from scipy import stats

import pymongo
from datetime import datetime
from datetime import timezone
from datetime import timedelta

import functions as func

def charts():
    data = [go.Bar(
        x=['giraffes', 'orangutans', 'monkeys'],
        y=[20, 14, 23] )]
    return data


#connect  to database
client = pymongo.MongoClient()
db = client.Invest
collection_price = db['DailyPrice']

#get distinct ticker
tickers = collection_price.distinct('Ticker')
tickers.sort()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    #row1
    html.Div(
        className = "row",
        children = [
            html.H1("Dashboard"),
            dcc.Dropdown(
                id='stock-ticker-input',
                options=[{'label': s[0], 'value': str(s[1])}for s in zip(tickers, tickers)],
                value=[],
                multi=False
            )
        ]
    ),

    #title
    html.Div(
        className = "row",
        children = [
            html.Div(
                className = "five columns",
                children = html.Div([html.H2("QQ Plot")])
            ),
            html.Div(
                className = "five columns",
                children = html.Div([html.H2("Beta to SPY")])
            )
        ]
    ),
    
    #row 2
    html.Div(
        className = "row",
        children = [
            html.Div(
                id = "QQ Plot",
                className="five columns",
            ),
            
            html.Div(
                    className="five columns",
                    children = html.Div([
                        dcc.Graph(id = 'figure2', figure = charts()),
                        ]
                    )
                )
            
        ]
    ),

    #row2
    html.Div(
        className = "row",
        children = [
            html.H2("Key Figures"),
            html.Div(
                className="three columns",
                children = html.Div([
                    html.H3("EY"),
                    dcc.Graph(id = 'figure3', figure = charts()),
                    ]
                )
            ),

            html.Div(
                className="two columns",
                children = html.Div([
                    html.H3("ROE"),
                    dcc.Graph(id = 'box1', figure = charts()),
                    ]
                )
            ),
            
            html.Div(
                    className="three columns",
                    children = html.Div([
                        html.H3("DY"),
                        dcc.Graph(id = 'figure4', figure = charts()),
                        ]
                    )
                ),
            
            html.Div(
                className="two columns",
                children = html.Div([
                    html.H3("ROE"),
                    dcc.Graph(id = 'box2', figure = charts()),
                    ]
                )
            ),
            
        ]
    ),

    #row3
    html.Div(
        className = "row",
        children = [
            html.H2(""),
            html.Div(
                className="three columns",
                children = html.Div([
                    html.H3("ROE"),
                    dcc.Graph(id = 'figure5', figure = charts()),
                    ]
                )
            ),

            html.Div(
                className="two columns",
                children = html.Div([
                    html.H3("ROE"),
                    dcc.Graph(id = 'box3', figure = charts()),
                    ]
                )
            ),
            
            html.Div(
                    className="three columns",
                    children = html.Div([
                        html.H3("PD"),
                        dcc.Graph(id = 'figure6', figure = charts()),
                        ]
                    )
                ),

            html.Div(
                className="two columns",
                children = html.Div([
                    html.H3("ROE"),
                    dcc.Graph(id = 'box4', figure = charts()),
                    ]
                )
            )
            
        ]
    ),

    #row4
    html.Div(
        className = "row",
        children = [
            html.Div(
                className="twlve columns",
                children = html.Div([
                    html.H2("Financial Statement"),
                    dcc.Graph(id = 'fs', figure = charts()),
                    ]
                )
            )
            
        ]
    ),

    #row5
    html.Div(
        className = "row",
        children = [
            html.Div(
                className="twlve columns",
                children = html.Div([
                    html.H2("Historical Price"),
                    dcc.Graph(id = 'HP', figure = charts()),
                    ]
                )
            )
            
        ]
    )
])

@app.callback(
    dash.dependencies.Output("QQ Plot",'children'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_graph(ticker):
    graphs = []
    if not ticker:
        graphs.append(html.H3(
            "Select a stock ticker.",
            style={'marginTop': 20, 'marginBottom': 20}
        ))
    else:
        X_lognorm = func.getPrices(collection_price, ticker, "close")
        X_lognorm = X_lognorm['close'].tolist()
        qq = stats.probplot(X_lognorm, dist='norm', sparams=(1))
        x = np.array([qq[0][0][0],qq[0][0][-1]])
        pts = go.Scatter(x=qq[0][0],
                        y=qq[0][1], 
                        mode = 'markers',
                        showlegend=False
                        )
        line = go.Scatter(x=x,
                        y=qq[1][1] + qq[1][0]*x,
                        showlegend=False,
                        mode='lines'
                        )

        data = [pts, line]
        layout = dict(xaxis = dict(zeroline = False,
                                linewidth = 1,
                                mirror = True),
                    yaxis = dict(zeroline = False, 
                                linewidth = 1,
                                mirror = True),
                    )

        fig = dict(data=data, layout=layout)
        graphs.append(dcc.Graph(id = 'figure1', figure = fig))
    return graphs

if __name__ == '__main__':
    app.run_server(debug=True)