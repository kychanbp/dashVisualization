# Trade Visualization and Execution Web App

A web app built on top of [Dash](https://github.com/plotly/dash) to visualize financial data, and manage trades and portfolio. Financial data is downloaded from [Interactive Brokers API](https://github.com/InteractiveBrokers/tws-api-public) using [ib_insync](https://github.com/erdewit/ib_insync). Data is stored in [MongoDB](https://www.mongodb.com/) with predefined schema. Portfolio management and trades are also done through [Interactive Brokers API](https://github.com/InteractiveBrokers/tws-api-public).

The web app is specific since data is stored in a specific format, and trades are made through Interactive Brokers only.

## Getting Started

### Prerequisites



## Features

### Dashboard

Dashboard is used to visualize data stored in [MongoDB](https://www.mongodb.com/). Visualization built includes 

* QQ Plot

* Beta to SPY
* 4 slots for visualizing data in financial statements
* A table to display financial statements
* A chart to display historical price data

Dashboard is also used to complete final check of target portfolio (as defined by users) by using the "passed", and "not passed" button in the end of page.

### Order Management

Order management tab lists detailed stocks information for stocks that passed the checking in Dashboard.

The tab also provides  a heat-map to visualize the correlation between stocks.

The calculate order amount button calculates the allocation to each stocks based on predefined principle amount, and it is assumed to be an equal portfolio.

The execute button sends signal to Interactive Brokers.

### Portfolio

Current portfolio section shows the current portfolio of all accounts.

Historical portfolio section shows the historical position of a particular stock within a particular period of time.

Equity curve shows the change of portfolio value with respect to time.

QQ plot shows the distribution of portfolio value compared to normal distribution.

## Demo



## Built with

* [Dash](https://github.com/plotly/dash) 
* [ib_insync](https://github.com/erdewit/ib_insync)

## Running the tests



## To-Dos

* Improve comments to make the code readable
* Write documentation
* Build a more general web app, including flexible brokers connection, flexible dashboard, etc

## Contributors

[John Chan](https://github.com/kychanbp): Self-taught "programmer" with an interest in Finance, Technology, and the Environment.







