#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  8 20:15:45 2025

@author: kalishamay
"""
import yfinance as yf
import requests
import matplotlib.pyplot as plt
#import pandas as pd


#declarables section
maxStockPrice = 20
# SEC ticker list
sec_url = "https://www.sec.gov/files/company_tickers.json"
headers = {
    'User-Agent': 'Kali Shamaly (shamalykali@gmail.com)',  # use real info
    'Accept': 'application/json',
    'Connection': 'keep-alive',
}

# Get tickers from SEC
res = requests.get(sec_url, headers=headers)
res.raise_for_status()
data = res.json()

# Extract first 10 tickers for demo
tickersLong = [item['ticker'] for item in list(data.values())[:]]
dataLong = {}
tickers = tickersLong[0:39]
for ticker in tickers:
    dataLong[ticker] = yf.Ticker(ticker).history(period = "3mo")#Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    
    