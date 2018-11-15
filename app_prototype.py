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
from datetime import date
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
collection_fs = db['FinancialStatement']

#get distinct ticker
tickers = collection_price.distinct('Ticker')
tickers.sort()

#get codes
codes_BAL = func.getCodes(collection_fs, "Annual", "BAL")
codes_INC = func.getCodes(collection_fs, "Annual", "INC")
codes_CAS = func.getCodes(collection_fs, "Annual", "CAS")
codes_ratios = ["DY", "PY", "ROE", "PD"]

dt = datetime.now()

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
                value="AAPL",
                multi=False
            ),

            dcc.DatePickerRange(
                id='my-date-picker-range',
                display_format='Y-M-D',
                start_date = date(dt.year, dt.month, dt.day)- timedelta(days=365.24),
                end_date = date(dt.year, dt.month, dt.day)
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
                children = [dcc.Graph(id = 'QQ Plot figure')]
            ),
            
            html.Div(
                id = "Beta",
                className="five columns",
                children = [dcc.Graph(id = 'Beta figure')]
            )       
        ]
    ),

    html.Div(
        className = "row",
        children = [
            html.H2("Key Figures"),
            html.Div(
                className="three columns",
                children = html.Div([
                    dcc.Dropdown(
                        id='BAL',
                        options=[{'label': s[0], 'value': str(s[1])}for s in zip(codes_BAL["Description"].tolist(), codes_BAL["Code"].tolist())],
                        value="AAPL",
                        multi=False
                        ),
                    ]
                )
            )
        ]
    ),

    #row2
    html.Div(
        className = "row",
        children = [
            html.Div(
                className="three columns",
                children = html.Div([
                    dcc.Graph(id = 'ratio1'),
                    ]
                )
            ),

            html.Div(
                className="two columns",
                children = html.Div([
                    dcc.Graph(id = 'ratio1_box'),
                    ]
                )
            ),
            
            html.Div(
                    className="three columns",
                    children = html.Div([
                        dcc.Graph(id = 'ratio2'),
                        ]
                    )
                ),
            
            html.Div(
                className="two columns",
                children = html.Div([
                    dcc.Graph(id = 'ratio2_box'),
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
    dash.dependencies.Output("QQ Plot figure",'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def QQ_graph(ticker, start_date, end_date):
    if start_date is not None and end_date is not None:
        X_lognorm = func.getPrices(collection_price, ticker, start_date, end_date, "close")
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
                    title = 'QQ Plot'
                    )

        fig = dict(data=data, layout=layout)
    else:
        fig = {}
    return fig

@app.callback(
    dash.dependencies.Output("Beta figure",'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date')])
def Beta_graph(ticker, start_date, end_date):
    if start_date is not None and end_date is not None:
        stock = func.getPrices(collection_price, ticker, start_date, end_date, "close")['close'].pct_change()[1:].values
        SPY = func.getPrices(collection_price, "SPY", start_date, end_date, "close")['close'].pct_change()[1:].values
        try:
            p = func.linreg(stock, SPY)

            pts = go.Scatter(x=SPY,
                            y=stock, 
                            mode = 'markers',
                            showlegend=False
                            )

            line = go.Scatter(x = SPY,
                            y = p[0] + p[1] * SPY,
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
                        title = 'Beta to SPY'
                        )

            fig = dict(data=data, layout=layout)
        except:
            fig = {}
    else:
        fig = {}
    return fig

@app.callback(
    dash.dependencies.Output("ratio1",'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('BAL', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date')])
def ratio1_graph(ticker, code, start_date, end_date):
    if start_date is not None and end_date is not None:
        data= func.getItems(collection_fs, ticker, start_date, end_date, "Annual", "BAL", code)
        try:
            bar = go.Bar(x=data['Date'].tolist(),
                        y=data[code].tolist(), 
                        )

            data = [bar]
                

            fig = dict(data=data)
        except:
            fig = {}
        
    else:
        fig = {}
    return fig

@app.callback(
    dash.dependencies.Output("ratio1_box",'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('BAL', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date')])
def ratio1_box_graph(ticker, code, start_date, end_date):
    if start_date is not None and end_date is not None:
        data= func.getItems(collection_fs, ticker, start_date, end_date, "Annual", "BAL", code)
        try:
            box = go.Box(y=data[code].tolist())

            data = [box]

            fig = dict(data=data)
        except:
            fig = {}
        
    else:
        fig = {}
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)