#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 21:59:21 2025

@author: kalishamay
"""

import requests  # Used to fetch SEC ticker data
from dash import html, callback, Output, Input, dash_table, register_page, dcc, State  # Dash components for building the app
import yfinance as yf  # Used for fetching historical stock data (commented-out portion)
from dash import Dash, dash_table
import pandas as pd
from collections import OrderedDict
from bs4 import BeautifulSoup
import math


register_page(__name__, path="/marketCheck/spyCheck", name="Market Status Check Based on SPY", order=0)

layout = html.Div(children=[
    html.H2("📥 Market Status Check Based on SPY", style={'textAlign': 'center'}),
    html.P("Enter duration to search"),
    dcc.Input(id='num1', type='number', placeholder='#'),
    dcc.Dropdown(
        id='unit1',
        options=[
            {'label': 'Days', 'value': 'd'},
            {'label': 'Weeks', 'value': 'w'},
            {'label': 'Months', 'value': 'm'},
            {'label': 'Years','value': 'y'}
        ],
        value=[],            # default value
        placeholder="Select a stock",
        clearable=True),
    html.P("Enter X Axis Interval"),
    dcc.Input(id='num2', type='number', placeholder='#'),
    dcc.Dropdown(
        id='unit2',
        options=[
            {'label': 'Days', 'value': 'd'},
            {'label': 'Weeks', 'value': 'w'},
            {'label': 'Months', 'value': 'm'},
            {'label': 'Years','value': 'y'}
        ],
        value=[],            # default value
        placeholder="Select a stock",
        clearable=True),
    html.Div([
        html.Button("Check", id="checkBtn", n_clicks=0)
    ], style={'textAlign': 'center', 'marginTop': '20px'}),
    html.Div(id = 'spyCheck'),
    ])
## inputs and outputs set now need logic for all scenarios and to add the plot

@callback(
    Output('spyCheck','children'),
    Input('checkBtn','n_clicks'),
    Input('num1','value'),
    Input('unit1','value'),
    Input('num2','value'),
    Input('unit2','value')
    )
def spyMarketCheck(n_clicks,num1,unit1,num2,unit2):
    url = "https://www.slickcharts.com/sp500"
    headers = {
    "User-Agent": "Mozilla/5.0 (compatible; KaliBot/1.0; +https://github.com/shamalykali)"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status() 
    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find("table", class_="table")
    tickers = []
    for row in table.find("tbody").find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 3:
            ticker = cols[2].get_text(strip=True)
            tickers.append(ticker)
            
    tickerData = {}
    durPull = num1
    if unit1 == "Days":
        useDur = durPull
    elif unit1 == "Weeks":
        useDur = round(durPull*5)
        useDur = math.floor(useDur)
    elif unit1 == "Months":
        useDur = round(durPull*20)
        useDur = math.floor(useDur)
    elif unit1 == "Years":
        useDur = round(durPull+240)
    
    if unit2 == "Days":
        useInterval = num2
    elif unit2 == "Weeks":
        useInterval = num2*5
    elif unit2 == "Months":
        useInterval = num2*20
    elif unit2 == "Years":
        useInterval = num2*240
    stockTally = 0
    for ticker in tickers:
        tempData = []
        tempData = yf.Ticker(ticker)
        # historyData = []
        historyData = tempData.history(period="10y")
        tickerData[ticker] = historyData
        tempData = []
        tempData = historyData["Close"].tail(useDur)
        
    numStocks = len(tickerData)
    percBeating = 100*(stockTally/numStocks)
    if n_clicks>0:
        # textOut = html.Div([
        #     html.H4(f"{percBeating}% of S&P 500 within 5% of their one month high")])
    # return textOut 
    
            
        # .sort_index().iloc[-1].to_dict()