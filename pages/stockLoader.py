# Import necessary libraries
import requests  # Used to fetch SEC ticker data
from dash import html, callback, Output, Input, dash_table, register_page, dcc  # Dash components for building the app
import yfinance as yf  # Used for fetching historical stock data (commented-out portion)
from dash import Dash, dash_table
import pandas as pd
from collections import OrderedDict

# Register this script as a page in a multi-page Dash app
register_page(__name__, path="/stockLoader", name="Stock Loader",order =1)

# Define layout for the page
layout = html.Div([
    # Title of the page
    html.H2("📥 Load SEC Stock Tickers", style={'textAlign': 'center'}),

    # Button to load tickers from SEC
    html.Div([
        html.Button("Click here to load tickers", id="loadBtn", n_clicks=0)
    ], style={'textAlign': 'center', 'marginTop': '20px'}),

    # Button to fetch price data (hidden by default)
    html.Div([
        html.Button("Read in ticker data", id="dataBtn", n_clicks=0, style={
            'display': 'none',  # Initially hidden until tickers are loaded
            'marginTop': '20px'
        })
    ], style={'textAlign': 'center'}),
    html.Div([
        html.Button("Write to watchlist", id="goToListBtn", n_clicks=0, style={
            'marginTop': '20px'
        })
    ], style={'textAlign': 'center'}),

    # Placeholder for output — like tables or error messages
    html.Div(id="outputContainer"),

    # Store component to hold the list of ticker names (for use between callbacks)
    dcc.Store(id="tickerNames"),

    # Placeholder Store for future use (e.g., price data)
    dcc.Store(id='tickerPrice'),
    dcc.Store(id='watchListData')
])

from dash import callback_context
import dash as dash

@callback(
    Output('loadBtn', 'style'),
    Output('outputContainer', 'children'),
    Output('dataBtn', 'style'),
    Output('tickerNames', 'data'),
    Output('tickerPrice', 'data'),
    Output('watchListData','data'),
    Input('loadBtn', 'n_clicks'),
    Input('dataBtn', 'n_clicks'),
    Input('tickerNames', 'data'),
    prevent_initial_call=True
)
def handle_all_stock_actions(load_clicks, data_clicks, tickers):
    watchList = {}
    ctx = callback_context
    triggered_id = ctx.triggered_id

    # Default return values
    hide_load_btn = dash.no_update
    output = dash.no_update
    show_data_btn = dash.no_update
    ticker_list = dash.no_update
    ticker_price_data = dash.no_update

    if triggered_id == 'loadBtn':
        # Step 1: Load tickers from SEC
        sec_url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            'User-Agent': 'Kali Shamaly (shamalykali@gmail.com)',
            'Accept': 'application/json',
            'Connection': 'keep-alive',
        }

        try:
            res = requests.get(sec_url, headers=headers)
            res.raise_for_status()
            data = res.json()
            data = {k: data[k] for k in list(data.keys())}

            tickersLong = [item['ticker'] for item in list(data.values())]
            

            tickers = [
                {
                    "Ticker": item.get("ticker", ""),
                    "Title": item.get("title", "")
                }
                for item in list(data.values())[:50]
            ]

            table = html.Div(
                dash_table.DataTable(
                    data=tickers,
                    columns=[{"name": col, "id": col} for col in ["Ticker", "Title"]],
                    style_table={
                        'height': '900px',
                        'overflowY': 'scroll',
                        'overflowX': 'auto',
                        'maxWidth': '100%',
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '5px',
                        'whiteSpace': 'normal',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': '200px'
                    },
                    style_header={'fontWeight': 'bold'},
                    page_size=100
                ),
                style={
                    'width': '33%',
                    'display': 'inline-block',
                    'verticalAlign': 'top',
                    'marginTop': '20px'
                }
            )

            hide_load_btn = {'display': 'none'}
            show_data_btn = {'display': 'inline-block'}
            output = table
            ticker_list = tickers

        except Exception as e:
            output = html.Div([
                html.P("❌ Failed to load data."),
                html.Pre(str(e))
            ])
            hide_load_btn = {'display': 'inline-block'}
            show_data_btn = {'display': 'none'}

    elif triggered_id == 'dataBtn' and tickers:
        # Step 2: Enrich tickers with stock prices using yfinance
        for i, item in enumerate(tickers):
            listCount = 0
            ticker = item['Ticker']
            try:
                dataTemp = yf.Ticker(ticker)
                hist = dataTemp.history(period='1y')
                currentPrice = round(hist['Close'][-1],2)
                tickers[i]['Price'] = currentPrice
                tickers[i]['52 Week High'] = round(hist['High'].max(),2)
                if currentPrice> (tickers[i]['52 Week High']-(tickers[i]['52 Week High']*0.05)):
                    tickers[i]['Within 5%?'] = "Yes"
                else:
                    tickers[i]['Within 5%?'] = "No"
                volume = hist['Volume'][-1]
                avgVol = hist['Volume'].mean()
                tickers[i]['Volume'] = volume
                tickers[i]['Average Volume'] = avgVol
                pe = []
                pe = dataTemp.info['forwardPE']
                tickers[i]['P/E Ratio'] = pe
                try:
                    tickers[i]["Price Change"] = round(hist['Close'].diff().mean(),2)
                    tickers[i]["Percent Change"] = 100*(round(hist['Close'].pct_change().mean() * 100,2))
                except:
                    tickers[i]["Price Change"] = "Not Available"
                    tickers[i]["Percent Change"]  = "Not Available"
            except:
                tickers[i]['Price'] = "Not Available"
                tickers[i]['52 Week High'] = "Not Available"
                tickers[i]["Volume"] = "Not Available"
                tickers[i]['Within 5%?'] = "Not Available"
                tickers[i]["Price Change"] = "Not Available"
                tickers[i]["Percent Change"] = "Not Available"
                tickers[i]['P/E Ratio'] =  "Not Available"
                tickers[i]["Average Volume"] = "Not Available"
            if (isinstance(tickers[i]["Price"], (int, float)) and 
                isinstance(tickers[i]["52 Week High"], (int, float))):
                if tickers[i]["Price"] >= tickers[i]["52 Week High"]:
                    listCount += 2
                if tickers[i]["Price"] >= tickers[i]["52 Week High"] - 0.05 * tickers[i]["52 Week High"]:
                    listCount += 1
                if tickers[i]["Volume"]>= tickers[i]["Average Volume"]:
                    listCount += 2
                if tickers[i]["Volume"]>= 100000:
                    listCount += 1
                if tickers[i]["Average Volume"]>= 100000:
                    listCount += 1
                if tickers[i]["Price Change"]>0:
                    listCount+=1
                if tickers[i]["Price Change"]>0.25:
                    listCount+=1
                if tickers[i]["Price Change"]>0.5:
                    listCount+=1
                if tickers[i]["Percent Change"]>0:
                    listCount+=1
                if tickers[i]["Percent Change"]>10:
                    listCount+=1
            if listCount >0:
                watchList[ticker] = tickers[i]
            tickers[i]["Watch List Count"] = listCount
                

        table = html.Div(
            dash_table.DataTable(
                data=tickers,
                columns=[{"name": col, "id": col} for col in ["Ticker", "Title", "Price", "Watch List Count","52 Week High", "Within 5%?","Volume", "Average Volume", "Price Change", "Percent Change"]],
                style_data_conditional = [
                {
                    "if": {
                        "filter_query": "{52 Week High} <= {Price}",
                        "column_id": "52 Week High",
                    },
                    "backgroundColor": "rgba(216, 252, 216, 0.659)",
                    "color": "black",
                },
                {
                    "if": {
                        "filter_query": "{52 Week High} > {Price}",
                        "column_id": "52 Week High",
                    },
                    "backgroundColor": "rgba(252, 160, 160, 0.529)",
                    "color": "black",
                },
                {
                    "if": {
                        "filter_query": "{Within 5%?} = 'Yes'",  
                        "column_id": "Within 5%?",
                    },
                    "backgroundColor": "rgba(216, 252, 216, 0.659)",
                    "color": "black",
                },
                {
                    "if": {
                        "filter_query": "{Within 5%?} = 'No'",  
                        "column_id": "Within 5%?",
                    },
                    "backgroundColor": "rgba(252, 160, 160, 0.529)",
                    "color": "black",
                },
                {
                    "if": {
                        "filter_query": "{Volume} >= {Average Volume}",  
                        "column_id": "Volume",
                    },
                    "backgroundColor": "rgba(216, 252, 216, 0.659)",
                    "color": "black",
                },
                {
                    "if": {
                        "filter_query": "{Volume} < {Average Volume}",  
                        "column_id": "Volume",
                    },
                    "backgroundColor": "rgba(252, 160, 160, 0.529)",
                    "color": "black",
                },
                {
                    "if": {
                        "filter_query": "{Average Volume} >= 100000",  
                        "column_id": "Average Volume",
                    },
                    "backgroundColor": "rgba(216, 252, 216, 0.659)",
                    "color": "black",
                },
                {
                    "if": {
                        "filter_query": "{Average Volume} < 100000",  
                        "column_id": "Average Volume",
                    },
                    "backgroundColor": "rgba(252, 160, 160, 0.529)",
                    "color": "black",
                },
                {
                    "if": {
                        "filter_query": "{Price Change} >= 0",  
                        "column_id": "Price Change",
                    },
                    "backgroundColor": "rgba(216, 252, 216, 0.659)",
                    "color": "black",
                },
                {
                    "if": {
                        "filter_query": "{Price Change} < 0",  
                        "column_id": "Price Change",
                    },
                    "backgroundColor": "rgba(252, 160, 160, 0.529)",
                    "color": "black",
                },
                {
                    "if": {
                        "filter_query": "{Percent Change} > 10",
                        "column_id": "Percent Change"},
                    "backgroundColor": "rgba(216,252,216,0.650)",
                    "color":"black"},
                {
                    "if":{
                        "filter_query": "{Percent Change} >= 0 && {Percent Change} < 10",
                        "column_id":"Percent Change"},
                    "backgroundColor":"rgba(255, 149, 0, 0.478)",
                    "color":"black"},
                {
                    "if": {
                        "filter_query": "{Percent Change} < 0",
                        "column_id": "Percent Change"},
                    "backgroundColor": "rgba(252, 160, 160, 0.529)",
                    "color": "black"
                },
            ],
                style_table={
                    'height': '900px',
                    'overflowY': 'scroll',
                    'overflowX': 'auto',
                    'maxWidth': '100%',
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'whiteSpace': 'normal',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': '200px'
                },
                style_header={'fontWeight': 'bold'},
                page_size=100
            ),
            style={
                'width': '100%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'marginTop': '20px'
            }
        )

        output = table
        ticker_price_data = tickers

    # At the end of the function:
    return hide_load_btn, output, show_data_btn, ticker_list, ticker_price_data, watchList


