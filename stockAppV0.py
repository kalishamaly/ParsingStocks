#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 28 11:26:47 2025

@author: kalishamaly
"""

import yfinance as yf
import requests
import plotly.graph_objs as go
#import pandas as pd
from datetime import datetime, timedelta
import pdb
from dash import Dash, html, dcc, callback, Output, Input, dash_table

#declarables section
maxStockPrice = 10
rangeUse = 100
exceedPerc = 1550

# SEC ticker list
sec_url = "https://www.sec.gov/files/company_tickers.json"
headers = {
    'User-Agent': 'Kali Shamaly (shamalykali@gmail.com)',  
    'Accept': 'application/json',
    'Connection': 'keep-alive',
}

today = datetime.today()
tilFriday = (4 - today.weekday() + 7)
tilFriday = tilFriday or 7
firstFriday  = today + timedelta(days=tilFriday)
fridays = [firstFriday + timedelta(weeks=i) for i in range(10)]



res = requests.get(sec_url, headers=headers)
res.raise_for_status()
data = res.json()


tickersLong = [item['ticker'] for item in list(data.values())[:]]
friDate = [fridays[i].date() for i in range(10)]

#initialize dictionaries
dataLong = {}
stockSubMaxList = {}
twoHunDayAvg = {}
sevenDayAvg = {}
fiveDayAvg = {}
oneHunDayAvg = {}
fiftyDayAvg = {}
thirtyDayAvg = {}
optionsData = {}
useStrike = {}
long200Seven = {}
long200Five = {}
long100Seven = {}
long100Five = {}
mid50Seven = {}
mid50Five = {}
short30Seven = {}
short30Five ={}
tickers = tickersLong[0:499]
for ticker in tickers:
    dataLong[ticker] = yf.Ticker(ticker).history(period = "1y")#Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    if dataLong[ticker]['Close'].empty:
        print("The {ticker} series is empty.")
    else:    
        closePrice = dataLong[ticker]['Close'][-1]
        if 'maxStockPrice' in locals():
            #pdb.set_trace()
            if closePrice<=maxStockPrice:
                stockSubMaxList[ticker] = closePrice
                sevenDay = dataLong[ticker]['Close'][-8:-1]
                sevenDayAvg[ticker] = sevenDay.mean()
                fiveDay = dataLong[ticker]['Close'][-6:-1]
                fiveDayAvg[ticker] = fiveDay.mean()
                twoHunDay = dataLong[ticker]['Close'][-201:-1]
                twoHunDayAvg[ticker] = twoHunDay.mean()
                if twoHunDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
                    long200Seven[ticker] = "Bull"
                else:
                    long200Seven[ticker] = "Bear"
                if twoHunDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
                    long200Five[ticker] = "Bull"
                else:
                    long200Five[ticker] = "Bear"
                oneHunDay = dataLong[ticker]['Close'][-101:-1]
                oneHunDayAvg[ticker] = oneHunDay.mean()
                if oneHunDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
                    long100Seven[ticker] = "Bull"
                else:
                    long100Seven[ticker] = "Bear"
                if oneHunDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
                    long100Five[ticker] = "Bull"
                else:
                    long100Five[ticker] = "Bear"
                fiftyDay = dataLong[ticker]['Close'][-51:-1]
                fiftyDayAvg[ticker] = fiftyDay.mean()
                if fiftyDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
                    mid50Seven[ticker] = "Bull"
                else:
                    mid50Seven[ticker]= "Bear"
                if fiftyDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
                    mid50Five[ticker] = "Bull"
                else:
                    mid50Five[ticker] = "Bear"
                thirtyDay = dataLong[ticker]['Close'][-31:-1]
                thirtyDayAvg[ticker] = thirtyDay.mean()
                if thirtyDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
                    short30Seven[ticker] = "Bull"
                else:
                    short30Seven[ticker] = "Bear"
                if thirtyDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
                    short30Five[ticker] = "Bull"
                else:
                    short30Five[ticker] = "Bear"
        else:
            stockSubMaxList[ticker] = closePrice
            sevenDay = dataLong[ticker]['Close'][-8:-1]
            sevenDayAvg[ticker] = sevenDay.mean()
            fiveDay = dataLong[ticker]['Close'][-6:-1]
            fiveDayAvg[ticker] = fiveDay.mean()
            twoHunDay = dataLong[ticker]['Close'][-201:-1]
            twoHunDayAvg[ticker] = twoHunDay.mean()
            if twoHunDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
                long200Seven[ticker] = "Bull"
            else:
                long200Seven[ticker] = "Bear"
            if twoHunDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
                long200Five[ticker] = "Bull"
            else:
                long200Five[ticker] = "Bear"
            oneHunDay = dataLong[ticker]['Close'][-101:-1]
            oneHunDayAvg[ticker] = oneHunDay.mean()
            if oneHunDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
                long100Seven[ticker] = "Bull"
            else:
                long100Seven[ticker] = "Bear"
            if oneHunDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
                long100Five[ticker] = "Bull"
            else:
                long100Five[ticker] = "Bear"
            fiftyDay = dataLong[ticker]['Close'][-51:-1]
            fiftyDayAvg[ticker] = fiftyDay.mean()
            if fiftyDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
                mid50Seven[ticker] = "Bull"
            else:
                mid50Seven[ticker]= "Bear"
            if fiftyDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
                mid50Five[ticker] = "Bull"
            else:
                mid50Five[ticker] = "Bear"
            thirtyDay = dataLong[ticker]['Close'][-31:-1]
            thirtyDayAvg[ticker] = thirtyDay.mean()
            if thirtyDayAvg[ticker]*((100+exceedPerc)/100)<sevenDayAvg[ticker]:
                short30Seven[ticker] = "Bull"
            else:
                short30Seven[ticker] = "Bear"
            if thirtyDayAvg[ticker]*((100+exceedPerc)/100)<fiveDayAvg[ticker]:
                short30Five[ticker] = "Bull"
            else:
                short30Five[ticker] = "Bear"
    
stocksPulled = list(short30Five.keys())
optionsCallChain = {}
companyNamesAll = {} 
closePrice = {}
historyAll = {}

for stock in stocksPulled:
    temp = yf.Ticker(stock)
    if 'longName' in temp.info:
        if temp.info['longName']:
            companyNamesAll[stock] = temp.info['longName']
            historyAll[stock] = temp.history(period = '1y')
            closePrice[stock] = historyAll[stock]['Close'][-1]
            expDates = temp.options
            optionsCallChain[stock] = {}
            for date in expDates:
                temp = yf.Ticker(stock).option_chain(date = date)
                optionsCallChain[stock][date] = temp.calls
        
        
    
################ App Portion ######################
###################################################
app = Dash()
app.layout= html.Div(children=[
    html.H1(children = "Parsing stocks to buy and sell calls on",style={'textAlign': 'center'}),
    html.Div(children=[
    "Ticker List",
    dcc.Dropdown(
        options=[{'label': ticker, 'value': ticker} for ticker in stocksPulled],
        id='stockDropdown',
        placeholder="Select a ticker")]),
        html.Div(style={'display': 'flex', 'gap': '10px'},
            children = [html.Div(id='stockSel',
                                 style = {'flex':'1'}),
                        html.Div(id='compName',
                                 style = {'flex':'1'}),
                        html.Div(id='latestStockPrice',
                                 style = {'flex':'1'}),
                        html.Div(id='trendImg', style={'flex': '1'})
                        ]
            ),
   dcc.RadioItems(["30 Days", "50 Days", "100 Days", "200 Days"],"30 Days",
                  id="historyLen"),
   dcc.Graph(id = 'historyPlot'),
   html.Div(id = "optionExpDates"),
   html.Div(id = "optionDisplay")
    ])
@callback(
    Output('stockSel','children'),
    Input('stockDropdown','value'))
def updateStock(value):
    return html.Span([
            html.B("Selected Ticker: "),
            value
        ])
@callback(
    Output('compName','children'),
    Input('stockDropdown','value'))
def getCompanyName(value):
    companyName = companyNamesAll[value]
    return html.B(companyName)

@callback(
    Output('latestStockPrice','children'),
    Input('stockDropdown','value'))
def getLatestPrice(value):
    stockPrice = closePrice[value]
    if stockPrice<0.01:
        stockPrice = round(stockPrice,6)
    elif stockPrice<0.1:
        stockPrice = round(stockPrice,4)
    elif stockPrice<1:
        stockPrice = round(stockPrice,3)
    else:
        stockPrice = round(stockPrice,2)
    return(html.Span([
        html.B('Stock Price: $'),
        stockPrice]))
@callback(
    Output('trendImg','children'),
    [Input('historyLen','value'),
     Input('stockDropdown','value')])
def displayTrendImg(day,stock):
    if day == "30 Days":
        stockTemp = thirtyDayAvg[stock]
    elif day == "50 Days":
        stockTemp = fiftyDayAvg[stock]
    elif day == "100 Days":
        stockTemp = oneHunDayAvg[stock]
    elif day == "200 Days":
        stockTemp = twoHunDayAvg[stock]
    percChange = (sevenDayAvg[stock]/stockTemp)*100
    if percChange > rangeUse:
        imgFile = 'greenArrow.jpeg'
    elif percChange < -rangeUse:
        imgFile = 'redArrow.jpeg'
    else:
        imgFile = 'neutral.jpg'

    return html.Img(src=f"/assets/{imgFile}", style={'height': '50px'})

@callback(
    Output('historyPlot','figure'),
    [Input('historyLen','value'),
     Input('stockDropdown','value')])
def plot_history(days, stock):
    stockHistoryLong = historyAll[stock]['Close']
    if days == "30 Days":
        stockHistory = stockHistoryLong[-31:-1]
    elif days == "50 Days":
        stockHistory = stockHistoryLong[-51:-1]
    elif days == "100 Days":
        stockHistory = stockHistoryLong[-101:-1]
    elif days == "200 Days":
        stockHistory = stockHistoryLong[-201:-1]
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stockHistory.index,
        y=stockHistory.values,
        mode='lines+markers',
        name=stock
    ))
    fig.update_layout(
        title=f"{stock} - {days} Price History",
        xaxis_title="Date",
        yaxis_title="Closing Price",
        height=300
    )
    fig.update_xaxes(range=[stockHistory.index[0], stockHistory.index[-1]])
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                       'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig.update_layout(height = 300)
    return fig

@callback(
    Output('optionExpDates','children'),
    Input('stockDropdown','value'))
def show_expirations(stock):
    if not stock or stock not in optionsCallChain:
        return html.Span("No expiration dates available.")
    
    expDates = list(optionsCallChain[stock].keys())
    if not expDates:
        return html.Span("No expiration dates found.")

    return dcc.RadioItems(
        id='expDateRadio',
        options=[{'label': d, 'value': d} for d in expDates],
        value=expDates[0]
    )
        
@callback(
    Output('optionDisplay','children'),
    [Input('stockDropdown','value'),
     Input('expDateRadio','value')])
def displayOptionsTable(stock, date):
    print(f"Options data for {stock} on {date}:\n", optionsCallChain[stock][date])
    if not stock or not date:
        return html.Span("Select a ticker and expiration date.")
    
    try:
        df = optionsCallChain[stock][date]
        if df.empty:
            return html.Span("No options data available for this date.")
        
        return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": col, "id": col} for col in df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'fontFamily': 'Arial'},
            page_size=10
        )
    except Exception as e:
        return html.Span(f"Error loading options data: {str(e)}")
app.run_server()
    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            