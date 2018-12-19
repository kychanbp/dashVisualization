from .server import app

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.plotly as py
import plotly.graph_objs as go

import pandas as pd
import numpy as np
from scipy import stats

import pymongo
from datetime import date
from datetime import datetime

import myproject.functions as func

import colorlover as cl

from subprocess import call

colorscale = cl.scales['9']['qual']['Paired']

#connect  to database
client = pymongo.MongoClient()
db = client.Invest
collection_price = db['DailyPrice']
collection_fs = db['FinancialStatement']
collection_ratios = db['KeyRatios']
collection_portfolio = db['TargetPortfolio']
collection_actualPortfolio = db['ActualPortfolio']
collection_account = db['AccountSummary']

#get distinct ticker
tickers = collection_price.distinct('Ticker')
tickers.sort()

def filteredTickers(db, date):
    query = [
        {"$match":{"date":date}},
        {"$match":{"$or":[{"Verify":None}]}}]
    cur = db.aggregate(query)
    df = pd.DataFrame(list(cur))
    tickers = df['Ticker'].tolist()
    tickers = list(set(tickers))
    tickers.sort()
    return tickers

#get codes
codes_BAL = func.getCodes(collection_fs, "Annual", "BAL")
codes_INC = func.getCodes(collection_fs, "Annual", "INC")
codes_CAS = func.getCodes(collection_fs, "Annual", "CAS")
codes_ratios = ["DY", "EY", "ROE", "PD"]

@app.callback(
    dash.dependencies.Output("stock-ticker-input",'options'),
    [dash.dependencies.Input('allOrFiltered', 'value'),
    dash.dependencies.Input('freezeDate', 'date')])
def update_dropdown(option, freezeDate):
    freezeDate = datetime.strptime(freezeDate, '%Y-%m-%d')
    opt = []
    if option == "All":
        opt = [{'label': s[0], 'value': str(s[1])}for s in zip(tickers, tickers)]
    elif option == "Filtered":
        try:
            tickers_filtered = filteredTickers(collection_portfolio, freezeDate)
            opt = [{'label': s[0], 'value': str(s[1])}for s in zip(tickers_filtered, tickers_filtered)]
        except:
            tickers_filtered = ''
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
        stock = func.getPrices(collection_price, ticker, start_date, end_date, "close")
        stock = stock.drop_duplicates()
        stock = stock['close'].pct_change()[1:].values
        SPY = func.getPrices(collection_price, "SPY", start_date, end_date, "close")
        SPY = SPY.drop_duplicates()
        SPY = SPY['close'].pct_change()[1:].values
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
    dash.dependencies.Output("FS",'columns'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('FS_dropdown', 'value')])
def update_fs_columns(ticker, statm):
    if ticker is not None:
        df = func.getStatements(collection_fs, ticker, '', '', 'Annual', statm)
        columns=[{"name": i, "id": i} for i in df.columns]
        return columns

@app.callback(
    dash.dependencies.Output("FS",'data'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('FS_dropdown', 'value')])
def update_fs_rows(ticker, statm):
    if ticker is not None:
        df = func.getStatements(collection_fs, ticker, '', '', 'Annual', statm)
        data=df.to_dict('records')
        return data

@app.callback(
    dash.dependencies.Output('HP','figure'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('my-date-picker-range', 'start_date'),
    dash.dependencies.Input('my-date-picker-range', 'end_date')])
def historical_price(ticker, start_date, end_date):

    dff = func.getPrices_all(collection_price, ticker, start_date, end_date)
    dff = dff.drop_duplicates()

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


@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('passed', 'n_clicks'),
    dash.dependencies.Input('freezeDate', 'date')])
def passed(ticker, n_clicks, freezeDate):
    if (n_clicks is not None) and (ticker is not None):
        freezeDate = datetime.strptime(freezeDate, '%Y-%m-%d')
        collection_portfolio.update_many({"Ticker":ticker}, {"$set" : {"Verify":1}})
        cur = collection_portfolio.aggregate([
            {"$match":{"Ticker":ticker}},{"$match":{"date":freezeDate}},{"$project":{"Verify":"$Verify"}},{"$limit":1}
        ])
        

@app.callback(
    dash.dependencies.Output('output-container-button-2', 'children'),
    [ dash.dependencies.Input('stock-ticker-input', 'value'),
    dash.dependencies.Input('notPassed', 'n_clicks'),
    dash.dependencies.Input('freezeDate', 'date')])
def notPassed(ticker ,n_clicks, freezeDate):
    freezeDate = datetime.strptime(freezeDate, '%Y-%m-%d')
    if (n_clicks is not None) and (ticker is not None):
        collection_portfolio.update_many({"Ticker":ticker}, {"$set" : {"Verify":0}})
        cur = collection_portfolio.aggregate([
            {"$match":{"Ticker":ticker}},{"$match":{"date":freezeDate}},{"$project":{"Verify":"$Verify"}},{"$limit":1}
        ])


#tab2
#
#
@app.callback(
    dash.dependencies.Output("verifiedPort",'columns'),
    [dash.dependencies.Input('dateRange_portfolio', 'start_date'),
    dash.dependencies.Input('dateRange_portfolio', 'end_date')])
def update_porfolio_columns(start_date, end_date):
    #connect  to database
    df = func.getPassedPortfolio(collection_portfolio)
    columns=[{"name": i, "id": i} for i in df.columns]
    return columns

@app.callback(
    dash.dependencies.Output("verifiedPort",'data'),
    [dash.dependencies.Input('dateRange_portfolio', 'start_date'),
    dash.dependencies.Input('dateRange_portfolio', 'end_date')])
def update_portfolio_rows(start_date, end_date):
    df = func.getPassedPortfolio(collection_portfolio)
    data=df.to_dict('records')
    return data

@app.callback(
    dash.dependencies.Output("correlation map",'figure'),
    [dash.dependencies.Input('dateRange_portfolio', 'start_date'),
    dash.dependencies.Input('dateRange_portfolio', 'end_date')])
def update_correlation_map(start_date, end_date):
    df = func.getPassedPortfolio(collection_portfolio)

    result = pd.DataFrame()
    for index, row in df.iterrows():
        lst = {}
        symbol = row['Ticker']
        price = func.getPrices(collection_price, symbol, start_date, end_date, 'close')
        price = price.drop_duplicates()

        try:
            lst[symbol] = price['close'].tolist()
            result = pd.concat([result, pd.DataFrame(lst)], axis = 1)
        except:
            result = pd.DataFrame(lst)
    
    cor = result.corr()
    arr = cor.values

    trace = go.Heatmap(z=arr, x = cor.columns, y = cor.columns)

    layout =  dict(height = 800, title = 'Stock Correlation')
    data=[trace]
    fig = dict(data = data, layout = layout)

    return fig

@app.callback(
    dash.dependencies.Output("output-container-button-4",'children'),
    [dash.dependencies.Input('calAmount', 'n_clicks')])
def orderAmount(n_clicks):
    #connect  to database
    if n_clicks is not None:
        call(["python", "myproject/order_amount.py"])
        return "Please Refresh"

@app.callback(
    dash.dependencies.Output("orderAmount",'columns'),
    [dash.dependencies.Input('Refresh_2', 'n_clicks')])
def orderAmount_columns_refresh(n_clicks):
    #connect  to database
    df = pd.read_csv("orderAmount.csv")
    columns=[{"name": i, "id": i} for i in df.columns]
    return columns

@app.callback(
    dash.dependencies.Output("orderAmount",'data'),
    [dash.dependencies.Input('Refresh_2', 'n_clicks')])
def orderAmount_rows_refresh(n_clicks):
    df = pd.read_csv("orderAmount.csv")
    data=df.to_dict('records')
    return data

@app.callback(
    dash.dependencies.Output("output-container-button-3",'children'),
    [dash.dependencies.Input('execute', 'n_clicks')])
def execute(n_clicks):
    if n_clicks is not None:
        call(["python", "myproject/execute.py"])
        return "Executed"



###tab3
@app.callback(
    dash.dependencies.Output("currentPort",'columns'),
    [dash.dependencies.Input('Refresh', 'n_clicks')])
def current_porfolio_columns(n_clicks):
    #connect  to database
    call(["python", "myproject/getCurrentPortfolio.py"])
    df = pd.read_csv("currentPortfolio.csv")
    columns=[{"name": i, "id": i} for i in df.columns]
    return columns

@app.callback(
    dash.dependencies.Output("currentPort",'data'),
    [dash.dependencies.Input('Refresh', 'n_clicks')])
def current_portfolio_rows(n_clicks):
    df = pd.read_csv("currentPortfolio.csv")
    data=df.to_dict('records')
    return data

@app.callback(
    dash.dependencies.Output("historicalPositions",'columns'),
    [dash.dependencies.Input('stock-ticker-input-positions', 'value'),
    dash.dependencies.Input('dateRange_positions', 'start_date'),
    dash.dependencies.Input('dateRange_positions', 'end_date')])
def update_actualPorfolio_columns(symbol, start_date, end_date):
    #connect  to database
    if symbol is not None:
        df = func.getHistoricalPortfolio(collection_actualPortfolio, symbol, start_date, end_date)
        columns=[{"name": i, "id": i} for i in df.columns]
        return columns

@app.callback(
    dash.dependencies.Output("historicalPositions",'data'),
    [dash.dependencies.Input('stock-ticker-input-positions', 'value'),
    dash.dependencies.Input('dateRange_positions', 'start_date'),
    dash.dependencies.Input('dateRange_positions', 'end_date')])
def update_actualPorfolio_rows(symbol, start_date, end_date):
    if symbol is not None:
        df = func.getHistoricalPortfolio(collection_actualPortfolio, symbol, start_date, end_date)
        data=df.to_dict('records')
        return data

@app.callback(
    dash.dependencies.Output("Equity Curve",'figure'),
    [dash.dependencies.Input('dateRange_positions', 'start_date'),
    dash.dependencies.Input('dateRange_positions', 'end_date')])
def equity_graph(start_date, end_date):
    if start_date is not None and end_date is not None:
        df = func.getAccoutValue(collection_account, "NetLiquidation")
        df = df[df['date']>=start_date]


        line = go.Scatter(x=df['date'],
                        y=df['value'],
                        showlegend=True,
                        mode='lines',
                        name='Equity Curve'
                        )

        
        data = [line]
        layout = dict(xaxis = dict(zeroline = False,
                                linewidth = 1,
                                mirror = True),
                    
                    yaxis = dict(zeroline = False, 
                                linewidth = 1,
                                mirror = True,
                                type = 'log',
                                ),
                    
                    title = 'Equity Curve'
                    )

        fig = dict(data=data, layout=layout)
    else:
        fig = {}
    return fig

@app.callback(
    dash.dependencies.Output("return",'figure'),
    [dash.dependencies.Input('dateRange_positions', 'start_date'),
    dash.dependencies.Input('dateRange_positions', 'end_date')])
def return_graph(start_date, end_date):
    if start_date is not None and end_date is not None:
        df = func.getReturn(collection_actualPortfolio, start_date)
        X_lognorm = df['return'].tolist()
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
                    title = 'QQ Plot of Return'
                    )

        fig = dict(data=data, layout=layout)
    else:
        fig = {}
    return fig

@app.callback(
    dash.dependencies.Output("ReturnSPY",'figure'),
    [dash.dependencies.Input('dateRange_positions', 'start_date'),
    dash.dependencies.Input('dateRange_positions', 'end_date')])
def returnVSSPY_graph(start_date, end_date):
    if start_date is not None and end_date is not None:
        df = func.getAccoutValue(collection_account, "NetLiquidation")
        df = df[df['date']>=start_date]

        """
        start_date = df['date'].tolist()
        start_date.sort()
        start_date = start_date[-5].strftime('%Y-%m-%d %H:%M:%S.%f')
        start_date = start_date.split(" ")[0]
        #print(start_date)
        """
        
        spy = func.getPrices(collection_price, 'SPY', start_date, end_date, 'close')
        spy = spy.drop_duplicates()

        bar = go.Bar(x=df['date'].tolist()[1:],
                    y=pd.to_numeric(df['value']).pct_change()[1:],
                    name = 'Equity',
                    )


        bar_spy = go.Bar(x=spy['date'].tolist()[1:],
                    y=spy['close'].pct_change()[1:],
                    name = 'SPY'
                    )

        data = [bar,bar_spy]

        layout = dict(
                    title = 'Return V.S SPY'
                    )
                
        fig = dict(data=data, layout = layout)
        
    else:
        fig = {}
    return fig
