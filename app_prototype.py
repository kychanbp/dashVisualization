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

import colorlover as cl

colorscale = cl.scales['9']['qual']['Paired']

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
collection_ratios = db['KeyRatios']
collection_portfolio = db['TargetPortfolio']

#get distinct ticker
tickers = collection_price.distinct('Ticker')
tickers.sort()

tickers_filtered = collection_portfolio.distinct('Ticker')
tickers_filtered.sort()

#get codes
codes_BAL = func.getCodes(collection_fs, "Annual", "BAL")
codes_INC = func.getCodes(collection_fs, "Annual", "INC")
codes_CAS = func.getCodes(collection_fs, "Annual", "CAS")
codes_ratios = ["DY", "EY", "ROE", "PD"]

dt = datetime.now()

all_options = {
    'All':[{'label': s[0], 'value': str(s[1])}for s in zip(tickers, tickers)]
,
    'Filtered': [{'label': s[0], 'value': str(s[1])}for s in zip(tickers_filtered, tickers_filtered)]
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    #row1
    html.Div(
        className = "row",
        children = [
            html.H1("Dashboard"),

            dcc.Checklist(
                id='allOrFiltered',
                options=[
                    {'label': 'All', 'value': 'All'},
                    {'label': 'Filtered', 'value': 'Filtered'},
                ],
                values=['All'],
                labelStyle={'display': 'inline-block'},
                ),

            dcc.Dropdown(
                id='stock-ticker-input',
                #options=[{'label': s[0], 'value': str(s[1])}for s in zip(tickers, tickers)],
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
                className="six columns",
                children = [dcc.Graph(id = 'QQ Plot figure')]
            ),
            
            html.Div(
                id = "Beta",
                className="six columns",
                children = [dcc.Graph(id = 'Beta figure')]
            )       
        ]
    ),

    html.Div(
        className = "row",
        children = [
            html.H2("Key Figures"),
            
                    ]
    ),

    #dropdown
    html.Div(
        className = "row",
        children = [
            html.Div(
                className="three columns",
                children = html.Div([
                    dcc.Dropdown(
                        id='BAL',
                        options=[{'label': s[0], 'value': str(s[1])}for s in zip(codes_BAL["Description"].tolist(), codes_BAL["Code"].tolist())],
                        value="ATCA",
                        multi=False
                        )
                    ])
            ),
            
            html.Div(className="three columns", children=html.Div([html.H2("")])),

            html.Div(
                className="three columns",
                children = html.Div([
                    dcc.Dropdown(
                        id='INC',
                        options=[{'label': s[0], 'value': str(s[1])}for s in zip(codes_INC["Description"].tolist(), codes_INC["Code"].tolist())],
                        value="SOPI",
                        multi=False
                        )
                    ])
            ),
        ]
    ),
    
        
    #row3 (plots)
    html.Div(
        className = "row",
        children = [
            html.Div(
                className="three columns",
                children = [
                    html.Div([dcc.Graph(id = 'ratio1'),])
                ]
            ),

            html.Div(
                className="three columns",
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
                className="three columns",
                children = html.Div([
                    dcc.Graph(id = 'ratio2_box'),
                    ]
                )
            ),
            
        ]
    ),

    #dropdown
    html.Div(
        className = "row",
        children = [
            html.Div(
                className="three columns",
                children = html.Div([
                    dcc.Dropdown(
                        id='CAS',
                        options=[{'label': s[0], 'value': str(s[1])}for s in zip(codes_CAS["Description"].tolist(), codes_CAS["Code"].tolist())],
                        value="OTLO",
                        multi=False
                        )
                    ])
            ),
            
            html.Div(className="three columns", children=html.Div([html.H2("")])),

            html.Div(
                className="three columns",
                children = html.Div([
                    dcc.Dropdown(
                        id='Key Ratios',
                        options=[{'label': s[0], 'value': str(s[1])}for s in zip(codes_ratios, codes_ratios)],
                        value="PD",
                        multi=False
                        )
                    ])
            ),
        ]
    ),

     #row3 (plots)
    html.Div(
        className = "row",
        children = [
            html.Div(
                className="three columns",
                children = [
                    html.Div([dcc.Graph(id = 'ratio3'),])
                ]
            ),

            html.Div(
                className="three columns",
                children = html.Div([
                    dcc.Graph(id = 'ratio3_box'),
                    ]
                )
            ),
            
            html.Div(
                    className="three columns",
                    children = html.Div([
                        dcc.Graph(id = 'ratio4'),
                        ]
                    )
            ),
            
            html.Div(
                className="three columns",
                children = html.Div([
                    dcc.Graph(id = 'ratio4_box'),
                    ]
                )
            ),
            
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
                    dcc.Graph(id = 'HP'),
                    ]
                )
            )
            
        ]
    )
])

@app.callback(
    dash.dependencies.Output("stock-ticker-input",'options'),
    [dash.dependencies.Input('allOrFiltered', 'values')])
def update_dropdown(option):
    opt = []
    if option == ["All"]:
        opt = [{'label': s[0], 'value': str(s[1])}for s in zip(tickers, tickers)]
    elif option == ["Filtered"]:
        opt = [{'label': s[0], 'value': str(s[1])}for s in zip(tickers_filtered, tickers_filtered)]
    return opt

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
            box = go.Box(y=data[code].tolist(), boxmean='sd')

            data = [box]

            fig = dict(data=data)
        except:
            fig = {}
        
    else:
        fig = {}
    return fig

@app.callback(
    dash.dependencies.Output("ratio2",'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('INC', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date')])
def ratio2_graph(ticker, code, start_date, end_date):
    if start_date is not None and end_date is not None:
        data= func.getItems(collection_fs, ticker, start_date, end_date, "Annual", "INC", code)
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
    dash.dependencies.Output("ratio2_box",'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('INC', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date')])
def ratio2_box_graph(ticker, code, start_date, end_date):
    if start_date is not None and end_date is not None:
        data= func.getItems(collection_fs, ticker, start_date, end_date, "Annual", "INC", code)
        try:
            box = go.Box(y=data[code].tolist(), boxmean='sd')

            data = [box]

            fig = dict(data=data)
        except:
            fig = {}
        
    else:
        fig = {}
    return fig

@app.callback(
    dash.dependencies.Output("ratio3",'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('CAS', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date')])
def ratio3_graph(ticker, code, start_date, end_date):
    if start_date is not None and end_date is not None:
        data= func.getItems(collection_fs, ticker, start_date, end_date, "Annual", "CAS", code)
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
    dash.dependencies.Output("ratio3_box",'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('CAS', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date')])
def ratio3_box_graph(ticker, code, start_date, end_date):
    if start_date is not None and end_date is not None:
        data= func.getItems(collection_fs, ticker, start_date, end_date, "Annual", "CAS", code)
        try:
            box = go.Box(y=data[code].tolist(), boxmean='sd')

            data = [box]

            fig = dict(data=data)
        except:
            fig = {}
        
    else:
        fig = {}
    return fig

@app.callback(
    dash.dependencies.Output("ratio4",'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('Key Ratios', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date')])
def ratio4_graph(ticker, code, start_date, end_date):
    if start_date is not None and end_date is not None:
        try:
            data= func.getRatios(collection_ratios, ticker, start_date, end_date, code)
            bar = go.Bar(x=data['date'].tolist(),
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
    dash.dependencies.Output("ratio4_box",'figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('Key Ratios', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date')])
def ratio4_box_graph(ticker, code, start_date, end_date):
    if start_date is not None and end_date is not None:
        try:
            data= func.getRatios(collection_ratios, ticker, start_date, end_date, code)
            box = go.Box(y=data[code].tolist(), boxmean='sd')

            data = [box]

            fig = dict(data=data)
        except:
            fig = {}
        
    else:
        fig = {}
    return fig

@app.callback(
    dash.dependencies.Output('HP','figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date')])
def historical_price(ticker, start_date, end_date):

    dff = func.getPrices_all(collection_price, ticker, start_date, end_date)

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
    
    
    data = [candlestick] + [Bar]
    layout =  {
            'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
            'legend': {'x': 0},
            'yaxis' : {'domain' : [0, 0.2]},
            'yaxis2' : {'domain':[0.2,0.8]}
    }
            
    fig = dict(data=data, layout = layout)

    return fig

if __name__ == '__main__':
    app.run_server(host="0.0.0.0",  port = "8080", debug=True)