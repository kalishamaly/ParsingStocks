#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 17:54:50 2024

@author: kalishamay
"""

#%%
import yfinance as yf
import pandas as pd
import csv
import io
from datetime import datetime, timedelta

today = datetime.today()

# Find the next Friday
days_until_friday = (4 - today.weekday()) % 7
next_friday = today + timedelta(days=days_until_friday)

# Find the following Friday
following_friday = next_friday + timedelta(days=7)
fridays = [next_friday.date(), following_friday.date()]  # Convert to date objects
file = "/Users/kalishamaly/Downloads/all_tickers.txt"

with open(file, "r") as file:
        file_contents = file.read()
        print(file_contents)

def get_option_prices(ticker, expiration_date):
    try:
        stock = yf.Ticker(ticker)
        options = stock.option_chain(expiration_date)
    except ValueError as e:
        print(f"Skipping ticker '{ticker}' for expiration date '{expiration_date}' because it encountered an error: {e}")
        return None  
    return options.calls, options.puts

def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    return stock.history(period="1d")["Close"][0]
stock_price = []
calls_table_upper = []
puts_table_lower = []

# Example usage
#ticker = "ACB"  # Ticker symbol for Apple Inc.
for ticker in file_contents.split('\n'):
    try:
        # Use each ticker symbol to get its stock price
        price = get_stock_price(ticker)
        var = [ticker,price]
        #stock_price+= "{:<20}{:<10}\n".format(var[0],var[1])
        stock_price.append(var)
    except IndexError:
        print(f"Skipping ticker '{ticker}' because it encountered an IndexError")
    for friday in fridays:
        date = friday.strftime("%Y-%m-%d")
        option_prices = get_option_prices(ticker, date)
    if option_prices is not None:
        calls, puts = option_prices
        Temp = calls[calls.strike > price].head(1)
        if not Temp.empty:
            lcuTemp = Temp.strike.iloc[0]  # Access the first value of the 'strike' column
            lpcuTemp = Temp.lastPrice.iloc[0]  # Access the first value of the 'lastPrice' column
            percDiff = 100 * (lpcuTemp / price)  # Calculate percentage difference
            callsUpper = [ticker, price, lcuTemp, lpcuTemp, percDiff]
            calls_table_upper.append(callsUpper)
        else:
            print("No calls found with strike price greater than the current price.")
        Templc = puts[puts.strike < price].head(1)
        if not Templc.empty:
            lclTemp = Templc.strike.iloc[0]  # Access the first value of the 'strike' column
            lpclTemp = Templc.lastPrice.iloc[0]  # Access the first value of the 'lastPrice' column
            percDiffcl = 100 * (lpclTemp / price)  # Calculate percentage difference
            callsLower = [ticker, price, lclTemp, lpclTemp, percDiffcl]
            puts_table_lower.append(callsLower)
        else:
            print("No calls found with strike price less than the current price.")
    else:
        print(f"Skipping ticker '{ticker}' for Friday '{friday}' because option prices are not available.")
            


