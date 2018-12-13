import time
start = time.time()

import asyncio
import pandas as pd
import pymongo
from datetime import datetime
from datetime import timezone
from datetime import timedelta

import functions as func

from ib_insync import *
ib = IB()
ib.connect('127.0.0.1', 4002, clientId=4)

client = pymongo.MongoClient()
db = client.Invest
collection_portfolio = db['TargetPortfolio']

def get_latest_date(db):
    date = db.distinct('date')
    date.sort()
    date = date[-1]
    return date

def get_latest_portf(db):
    date = get_latest_date(db)
    query = [
        {"$match":{"date": date}},

    ]
    cursor = db.aggregate(query)
    df = pd.DataFrame(list(cursor))
    df.set_index('Ticker', inplace = True)

    return df

def order_target_percent(stocks, current_positions, size):
    try:
        current_positions['Symbol'] = current_positions['contract'].apply(lambda x: x.symbol)
    except:
        current_positions = pd.DataFrame(columns = ['Symbol'])
  
    avgsize = size/(len(stocks))

    #get targeted symbol which also exits in current positions
    intersect = list(set(stocks['Ticker']) & set(current_positions['Symbol'].tolist()))

    #target side
    target_side = list(set(stocks['Ticker']) - set(intersect))

    #current portfolio side
    current_portfolio_side = list(set(current_positions['Symbol'].tolist()) - set(intersect))

    lst = []
    for index, row in current_positions[current_positions['Symbol'].isin(intersect)].iterrows():

        contract = Stock(row['contract'].symbol, "SMART", "USD", primaryExchange= row['contract'].exchange)
        ib.qualifyContracts(contract)

        ib.reqMktData(contract, '', True, False)
        bar_value = ib.ticker(contract)
        ib.sleep(2)

        data = bar_value.marketPrice()
        print("Adjusting: {}:{}".format(row['contract'].symbol, data))

        symbol = row['contract'].symbol
        exchange = row['contract'].exchange
        position = row['position']

        temp = {}
        try:
            order_size = int(avgsize/data) -position
        except:
            order_size = (avgsize/data) -position
        temp["Symbol"] = symbol
        temp["Exchange"] = exchange
        temp["order_size"] = order_size

        lst.append(temp)
    
    for index, row in current_positions[current_positions['Symbol'].isin(current_portfolio_side)].iterrows():
        symbol = row['contract'].symbol
        exchange = row['contract'].exchange
        position = row['position']

        temp = {}
        order_size = -position
        temp["Symbol"] = symbol
        temp["Exchange"] = exchange
        temp["order_size"] = order_size

        lst.append(temp)

        print("Removing {}".format(symbol))

    for index, row in stocks[stocks['Ticker'].isin(target_side)].iterrows():

        contract = Stock(row['Ticker'], "SMART", "USD", primaryExchange= row['Primary Exchange'])
        ib.qualifyContracts(contract)

        ib.reqMktData(contract, '', True, False)
        bar_value = ib.ticker(contract)
        ib.sleep(2)

        data = bar_value.marketPrice()
        print("Purchasing {}:{}".format(row['Ticker'], data))

        symbol = row['Ticker']
        exchange = row['Primary Exchange']

        temp = {}
        try:
            order_size = int(avgsize/data)
        except:
            order_size = avgsize/data
        temp["Symbol"] = symbol
        temp["Exchange"] = exchange
        temp["order_size"] = order_size

        lst.append(temp)

    df = pd.DataFrame(lst)
    df = df.drop_duplicates() 
    
    return df

df_positions = pd.DataFrame(ib.positions())
#print(df_positions)
portfolio = func.getPassedPortfolio(collection_portfolio)
#print(portfolio)
amount = [v for v in ib.accountValues() if v.tag == 'NetLiquidation'][0].value
amount = float(amount)
order_cal = order_target_percent(portfolio, df_positions, amount *0.9)

order_cal.to_csv("orderAmount.csv", index=False)