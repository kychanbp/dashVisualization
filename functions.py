import pandas as pd

def getPrices(collection, symbol, field):
    query = [
        {"$match":{"Ticker":symbol}},
        {"$project":{"_id" : 0, "Ticker":"$Ticker", "date":"$date", "{}".format(field):"${}".format(field)}}
    ]

    cursor = collection.aggregate(query)
    df = pd.DataFrame(list(cursor))
    df.set_index("Ticker", inplace = True)

    return df
