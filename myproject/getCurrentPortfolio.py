import pandas as pd
from ib_insync import *
ib = IB()
ib.connect('127.0.0.1', 4002, clientId=5) 

def getCurrentPotfolio(ib):
    df = pd.DataFrame(ib.portfolio())
    try:
        df['Ticker'] = df['contract'].apply(lambda x: x.symbol)
        df['Exchange'] = df['contract'].apply(lambda x: x.primaryExchange)
        df.drop(columns = ['contract'], inplace=True)
        df = df[['account','Ticker','Exchange','position','marketPrice','averageCost','unrealizedPNL','realizedPNL']]
    except:
        df = pd.DataFrame(columns = ['account','Ticker','Exchange','position','marketPrice','averageCost','unrealizedPNL','realizedPNL'])
    return df

df = getCurrentPotfolio(ib)

df.to_csv("currentPortfolio.csv", index=False)