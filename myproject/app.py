from .server import app, server
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pymongo
from datetime import datetime
from datetime import date
from datetime import timezone
from datetime import timedelta

import myproject.functions as func

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
app.config['suppress_callback_exceptions']=True

app.layout = html.Div([
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Dashboard', value='tab-1'),
        dcc.Tab(label='Portfolio', value='tab-2'),
        dcc.Tab(label='Order Management', value='tab-3')
    ]),
    html.Div(id='tabs-content')
])

tab_1 = html.Div([
    #row1
    html.Div(
        className = "row",
        children = [
            dcc.RadioItems(
                id='allOrFiltered',
                options=[
                    {'label': 'All', 'value': 'All'},
                    {'label': 'Filtered', 'value': 'Filtered'},
                ],
                value='All',
                labelStyle={'display': 'inline-block'},
                ),
            
            dcc.Dropdown(
                id='stock-ticker-input',
                #options=[{'label': s[0], 'value': str(s[1])}for s in zip(tickers, tickers)],
                value="AAPL",
                multi=False,
                clearable=False
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
                        multi=False,
                        clearable=False
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
                        multi=False,
                        clearable=False
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
                        multi=False,
                        clearable=False
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
                        multi=False,
                        clearable=False
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

    #heading
    html.Div(
        className = "row",
        children = [
            html.Div(
                className="twlve columns",
                children = html.Div([
                    html.H2("Financial Statement"),
                    ]
                )
            )
            
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
                        id='FS_dropdown',
                        options=[{'label': s[0], 'value': str(s[1])}for s in zip(['BAL', 'INC', 'CAS'],['BAL', 'INC', 'CAS'])],
                        value="CAS",
                        multi=False,
                        clearable=False
                        )
                    ])
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
                    dash_table.DataTable(id = 'FS'),
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

@app.callback(dash.dependencies.Output('tabs-content', 'children'),
              [dash.dependencies.Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return tab_1
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])

from . import callbacks_data