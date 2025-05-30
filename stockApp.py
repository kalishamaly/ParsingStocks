#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  8 20:15:45 2025

@author: kalishamay
"""
import yfinance as yf
import requests
#import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta


#declarables section
maxStockPrice = 40
rangeUse = 50

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
optionsData = {}
useStrike = {}
tickers = tickersLong[0:99]
for ticker in tickers:
    dataLong[ticker] = yf.Ticker(ticker).history(period = "1y")#Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    closePrice = dataLong[ticker]['Close'][-1]
    if closePrice<=maxStockPrice:
        stockSubMaxList[ticker] = closePrice
        dataTemp = yf.Ticker(ticker)
        optionsData[ticker] = {}
        useStrike[ticker] = {}
        useStrike[ticker]['calls'] ={}
        useStrike[ticker]['puts'] = {}
        optionsData[ticker]['calls'] ={}
        optionsData[ticker]['puts'] = {}
        for week in friDate:
            week = week.strftime('%Y-%m-%d')
            callStrikes = []
            try:
                optionsData[ticker]['calls'][week] = dataTemp.option_chain(date=week).calls
                optionsData[ticker]['calls'][week]['lastPrice'] = optionsData[ticker]['calls'][week]['lastPrice']-1
                spC = optionsData[ticker]['calls'][week]['strike']
                callMean = spC.mean()
                useStrike[ticker]['calls'][week] = optionsData[ticker]['calls'][week][(spC > (1 - rangeUse / 100) * callMean) & (spC < (1 + rangeUse / 100) * callMean)]
            except ValueError:
                pass
            try:
                optionsData[ticker]['puts'][week] = dataTemp.option_chain(date=week).puts
                optionsData[ticker]['puts'][week]['lastPrice'] = optionsData[ticker]['puts'][week]['lastPrice']-1
                spP = optionsData[ticker]['puts'][week]['strike']
                putMean = spP.mean()
                useStrike[ticker]['puts'][week] = spP[(spP > (1 - rangeUse / 100) * putMean) & (spP < (1 + rangeUse / 100) * putMean)]
            except ValueError:
                pass