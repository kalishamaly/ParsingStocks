#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 19:00:45 2025

@author: kalishamay
"""





# Import necessary libraries
import requests  # Used to fetch SEC ticker data
from dash import html, callback, Output, Input, dash_table, register_page, dcc  # Dash components for building the app
import yfinance as yf  # Used for fetching historical stock data (commented-out portion)

# Register this script as a page in a multi-page Dash app
register_page(__name__, path="/stockLoader", name="Stock Loader")

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

    # Placeholder for output — like tables or error messages
    html.Div(id="outputContainer"),

    # Store component to hold the list of ticker names (for use between callbacks)
    dcc.Store(id="tickerNames"),

    # Placeholder Store for future use (e.g., price data)
    dcc.Store(id='tickerPrice')
])

from dash import callback_context
import dash as dash

@callback(
    Output('loadBtn', 'style'),
    Output('outputContainer', 'children'),
    Output('dataBtn', 'style'),
    Output('tickerNames', 'data'),
    Output('tickerPrice', 'data'),
    Input('loadBtn', 'n_clicks'),
    Input('dataBtn', 'n_clicks'),
    Input('tickerNames', 'data'),
    prevent_initial_call=True
)
def handle_all_stock_actions(load_clicks, data_clicks, tickers):
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
            data = {k: data[k] for k in list(data.keys())[0:20]}

            tickersLong = [item['ticker'] for item in list(data.values())]

            tickers = [
                {
                    "Ticker": item.get("ticker", ""),
                    "Title": item.get("title", "")
                }
                for item in data.values()
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
            ticker = item['Ticker']
            try:
                dataTemp = yf.Ticker(ticker)
                hist = dataTemp.history(period='1y')
                currentPrice = round(hist['Close'][-1],2)
                tickers[i]['Price'] = currentPrice
                tickers[i]['52 Week High'] = round(hist['High'].max(),2)
                if currentPrice> ((tickers[i]['52 Week High']*0.05)+tickers[i]['52 Week High']):
                    tickers[i]['Within 5%?'] = "Yes"
                else:
                    tickers[i]['Within 5%?'] = "No"
            except:
                tickers[i]['Price'] = "Not Available"
                tickers[i]['Max'] = "Not Available"
                tickers[i]['Within 5%'] = "Not Available"


        table = html.Div(
            dash_table.DataTable(
                data=tickers,
                columns=[{"name": col, "id": col} for col in ["Ticker", "Title", "Price", "52 Week High"," Within 5%?"]],
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

    return hide_load_btn, output, show_data_btn, ticker_list, ticker_price_data


# @callback(
#     [Output('loadBtn', 'style'),              # Hide the load button after click
#      Output('outputContainer', 'children'),   # Display table or error
#      Output('dataBtn','style'),               # Show the next button
#      Output('tickerNames','data')],           # Store list of tickers (just the symbols)
#     Input('loadBtn', 'n_clicks'),
#     prevent_initial_call=True  # Prevent triggering on initial page load
# )
# def loadStockTickerList(n_clicks):
#     sec_url = "https://www.sec.gov/files/company_tickers.json"  # URL to SEC's ticker data

#     # Headers to avoid SEC's 403 error (they require a valid user-agent)
#     headers = {
#         'User-Agent': 'Kali Shamaly (shamalykali@gmail.com)',
#         'Accept': 'application/json',
#         'Connection': 'keep-alive',
#     }

#     try:
#         # Fetch the ticker list
#         res = requests.get(sec_url, headers=headers)
#         res.raise_for_status()  # Raise error for bad status codes
#         data = res.json()  # Convert JSON response into Python dict

#         # Extract a flat list of ticker symbols (for future price lookup)
#         tickersLong = [item['ticker'] for item in list(data.values())[0:100]]

#         # Create a list of dicts with ticker and title (for display in table)
#         tickers = [
#             {
#                 "Ticker": item.get("ticker", ""),
#                 "Title": item.get("title", "")
#             }
#             for item in data.values()
#         ]

#         # Create a styled Dash DataTable
#         table = html.Div(
#             dash_table.DataTable(
#                 data=tickers,
#                 columns=[{"name": col, "id": col} for col in ["Ticker", "Title"]],
#                 style_table={
#                     'height': '900px',
#                     'overflowY': 'scroll',
#                     'overflowX': 'auto',
#                     'maxWidth': '100%',
#                 },
#                 style_cell={
#                     'textAlign': 'left',
#                     'padding': '5px',
#                     'whiteSpace': 'normal',
#                     'overflow': 'hidden',
#                     'textOverflow': 'ellipsis',
#                     'maxWidth': '200px'
#                 },
#                 style_header={'fontWeight': 'bold'},
#                 page_size=100  # Optional: pagination
#             ),
#             style={
#                 'width': '33%',
#                 'display': 'inline-block',
#                 'verticalAlign': 'top',
#                 'marginTop': '20px'
#             }
#         )

#         # Return updated states:
#         return {'display': 'none'}, table, {'display': 'inline-block'}, tickers

#     except Exception as e:
#         # Handle errors (network issues, bad data, etc.)
#         return {'display': 'inline-block'}, html.Div([
#             html.P("❌ Failed to load data."),
#             html.Pre(str(e))  # Show the error message
#         ])


# @callback([Output('outputContainer','children'), #dash table
#       Output('tickerPrice','data')], #save price of tickers
#     [Input('dataBtn','n_clicks'), #use load data button
#       Input('tickerNames','data')]) #read inthe triggers 

# def loadStockPriceHistory(n_clicks,tickers): #function to load stock prices
#     tickersLong = [item['ticker'] for item in list(tickers)] #tickers only
#     for i,ticker in enumerate(tickersLong):
#         try:
#             dataTemp = yf.Ticker(ticker) #load data
#             periodTemp = dataTemp.history(period = '5d') #get last 5 days
#             currentPrice = periodTemp['Close'][-1] #get latest price
#             tickers[i]['Price'] = currentPrice
#         except:
#             tickers[i]['Price'] = "Not Available"
#     table = html.Div(
#         dash_table.DataTable(
#             data=tickers,
#             columns=[{"name": col, "id": col} for col in ["Ticker", "Title", "Price"]],
#             style_table={
#                 'height': '900px',
#                 'overflowY': 'scroll',
#                 'overflowX': 'auto',
#                 'maxWidth': '100%',
#             },
#             style_cell={
#                 'textAlign': 'left',
#                 'padding': '5px',
#                 'whiteSpace': 'normal',
#                 'overflow': 'hidden',
#                 'textOverflow': 'ellipsis',
#                 'maxWidth': '200px'
#             },
#             style_header={'fontWeight': 'bold'},
#             page_size=100  # Optional: pagination
#         ),
#         style={
#             'width': '33%',
#             'display': 'inline-block',
#             'verticalAlign': 'top',
#             'marginTop': '20px'
#         }
#     )
#     return table, tickers      
            
        
        
# @callback(
#     [Output('outputContainer','style'),
#       Output('tickerHistory','data')],
#     [Input('dataBtn','n_clicks'),
#       Input('tickerNames','data')],
#     prevent_initial_call=True
# )
# def loadStockPriceHistory(n_clicks, tickers):
#     if not tickers:
#         return {'display': 'inline-block'}, {}

#     # Limiting number of tickers for demo/performance
#     tickers = tickers[:10]
#     historyData = {}
#     summaries = []

#     for ticker in tickers:
#         try:
#             data = yf.Ticker(ticker).history(period='1y')
#             if data.empty:
#                 summaries.append(f"{ticker}: No data available.")
#                 continue
#             historyData[ticker] = data.to_dict()
#             price = data['Close'][-1]
#             summaries.append(f"{ticker}: Current price is ${round(price, 2)}")
#         except Exception as e:
#             summaries.append(f"{ticker}: Failed to load data ({str(e)})")

#     output = html.Ul([html.Li(msg) for msg in summaries])

#     return {'display': 'inline-block'}, historyData

