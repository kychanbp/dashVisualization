import pandas as pd

from datetime import datetime
from datetime import timezone
from datetime import timedelta

from statsmodels import regression
import statsmodels.api as sm
import math
import numpy as np
import pymongo

def getPrices(collection, symbol, start, end, field):
    query = [
        {"$match":{"Ticker":symbol}},
        {"$match":{"date":{"$lte": datetime.strptime(end, '%Y-%m-%d'), "$gte": datetime.strptime(start, '%Y-%m-%d')}}},
        {"$project":{"_id" : 0, "Ticker":"$Ticker", "date":"$date", "{}".format(field):"${}".format(field)}}
    ]

    cursor = collection.aggregate(query)
    df = pd.DataFrame(list(cursor))
    df.set_index("Ticker", inplace = True)

    return df

def getPrices_all(collection, symbol, start, end):
    query = [
        {"$match":{"Ticker":symbol}},
        {"$match":{"date":{"$lte": datetime.strptime(end, '%Y-%m-%d'), "$gte": datetime.strptime(start, '%Y-%m-%d')}}},
        #{"$project":{"_id" : 0, "Ticker":"$Ticker", "date":"$date"}}
    ]

    cursor = collection.aggregate(query)
    df = pd.DataFrame(list(cursor))
    df.set_index("Ticker", inplace = True)

    return df

def linreg(x,y):
    # We add a constant so that we can also fit an intercept (alpha) to the model
    # This just adds a column of 1s to our data
    x = sm.add_constant(x)
    model = regression.linear_model.OLS(y,x).fit()
    # Remove the constant now that we're done
    x = x[:, 1]
    return model.params

def getCodes(collection, period, statm):
    query = [
        {"$unwind":"${}".format(period)},
        {"$project":{"{}".format(statm):{"$objectToArray":"${}.{}".format(period, statm)}}},
        {"$unwind":"${}".format(statm)},
        {"$project":{"Code":"${}.k".format(statm), "Description":"${}.v.Description".format(statm)}},
        {"$group":{"_id":{"Code":"$Code", "Description":"$Description"}}},
        {"$replaceRoot":{"newRoot":"$_id"}}
    ]

    cursor = collection.aggregate(query)
    df = pd.DataFrame(list(cursor))

    return df
    
def getItems(collection, symbol, start, end, period, statm, code):
    query =[
    {"$project":{"Ticker":1, "{}.Date".format(period):1,"{}.{}.{}.Value".format(period, statm, code):1}},
    {"$unwind":"${}".format(period)},
    {"$match":{"Ticker":symbol}},
    #{"$match":{"{}.Date".format(period):{"$lte": datetime.strptime(end, '%Y-%m-%d'), "$gte": datetime.strptime(start, '%Y-%m-%d')}}},
    {"$group":{"_id":{"Ticker":"$Ticker","Date":"${}.Date".format(period) ,code:"${}.{}.{}.Value".format(period, statm, code)}}},
    {"$replaceRoot": { "newRoot": "$_id" }}
    ]

    cursor = collection.aggregate(query)
    df = pd.DataFrame(list(cursor))
    df.set_index('Ticker', inplace = True)
    df.sort_values('Date', inplace = True)
    return df[-5:]

def getRatios(collection, symbol, start, end, ratio):
    query = [
        {"$match":{"Ticker":symbol}},
        {"$match":{"date":{"$lte": datetime.strptime(end, '%Y-%m-%d'), "$gte": datetime.strptime(start, '%Y-%m-%d')}}},
        {"$project":{"Ticker":1, "date":1, ratio:1}}
    ]

    cursor = collection.aggregate(query)
    df = pd.DataFrame(list(cursor))
    df.set_index('Ticker', inplace = True)
    df.sort_values('date', inplace = True)

    return df

"""
client = pymongo.MongoClient()
db = client.Invest
collection = db['DailyPrice']

print(getPrices_all(collection, "GE", "2018-01-01", "2018-12-31"))
"""