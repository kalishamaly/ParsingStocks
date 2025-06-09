#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 19:00:45 2025

@author: kalishamay
"""


import requests
from dash import html, callback, Output, Input, dash_table, register_page, dcc
import yfinance as yf

register_page(__name__, path="/stockLoader", name="Stock Loader")

layout = html.Div([
    html.H2("📥 Load SEC Stock Tickers", style={'textAlign': 'center'}),

    html.Div([
        html.Button("Click here to load tickers", id="loadBtn", n_clicks=0)
    ], style={'textAlign': 'center', 'marginTop': '20px'}),

    html.Div([
        html.Button("Read in ticker data", id="dataBtn", n_clicks=0, style={
            'display': 'none',
            'marginTop': '20px'
        })
    ], style={'textAlign': 'center'}),

    html.Div(id="outputContainer"),
    dcc.Store(id="tickerNames"),
    dcc.Store(id='tickerHistory')
])

@callback(
    [Output('loadBtn', 'style'),
     Output('outputContainer', 'children'),
     Output('dataBtn','style'),
     Output('tickerNames','data')],
    Input('loadBtn', 'n_clicks'),
    prevent_initial_call=True
)
def loadStockTickerList(n_clicks):
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

        tickersLong = [item['ticker'] for item in list(data.values())[:]]
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
                'display': 'inline-block',  # keeps it inline if you add other blocks later
                'verticalAlign': 'top',
                'marginTop': '20px'
            }
        )

        return {'display': 'none'}, table, {'display': 'inline-block'}, tickersLong

    except Exception as e:
        return {'display': 'inline-block'}, html.Div([
            html.P("❌ Failed to load data."),
            html.Pre(str(e))
        ])
    
@callback(
    [Output('outputContainer','style'),
     Output('tickerHistory','data')],
    [Input('dataBtn','n_clicks'),
     Input('tickerNames','data')],
    prevent_initial_call=True
)
def loadStockPriceHistory(n_clicks, tickers):
    if not tickers:
        return {'display': 'inline-block'}, {}

    # Limiting number of tickers for demo/performance
    tickers = tickers[:10]
    historyData = {}
    summaries = []

    for ticker in tickers:
        try:
            data = yf.Ticker(ticker).history(period='1y')
            if data.empty:
                summaries.append(f"{ticker}: No data available.")
                continue
            historyData[ticker] = data.to_dict()
            price = data['Close'][-1]
            summaries.append(f"{ticker}: Current price is ${round(price, 2)}")
        except Exception as e:
            summaries.append(f"{ticker}: Failed to load data ({str(e)})")

    output = html.Ul([html.Li(msg) for msg in summaries])

    return {'display': 'inline-block'}, historyData

