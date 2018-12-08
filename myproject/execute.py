import pandas as pd 

from ib_insync import *
ib = IB()
ib.connect('127.0.0.1', 4002, clientId=6)

def order(df):
    for index, row in df.iterrows():
        contract = Stock(row['Symbol'], "SMART", "USD", primaryExchange= row['Exchange'])
        ib.qualifyContracts(contract)

        amount = row['order_size']
        
        if amount >0:
            order = MarketOrder('BUY', amount)
            ib.placeOrder(contract, order)
        elif amount <0:
            order = MarketOrder('SELL', amount)
            ib.placeOrder(contract, order)
        else:
            print(amount)

df = pd.read_csv("orderAmount.csv")
order(df)