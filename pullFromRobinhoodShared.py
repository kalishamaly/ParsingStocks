#&&
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 15:22:21 2024

@author: kalishamay
"""
import pdb
email = ""
password = ""
from datetime import datetime, timedelta
import robin_stocks.robinhood as robin

# Define your Robinhood login credentials
# Log in to Robinhood
robin.login(email, password)
minPrice = 1
lowLim = -1
upLim = 1
# Define the path to the file containing ticker symbols
file_path = "/Users/kalishamaly/Downloads/all_tickers.txt"

# Define the second Friday date
today = datetime.today()
days_until_friday = (4 - today.weekday()) % 7
next_friday = today + timedelta(days=days_until_friday)
following_friday = next_friday + timedelta(days=7)
fridays = [next_friday.date(), following_friday.date()]


with open(file_path, "r") as file:
    # Read the contents of the file
    content = file.read()

    # Split the content into lines
    lines = content.splitlines()  # or lines = content.split('\n')
    lines = [line for line in lines if len(line) <= 4]
    
# Initialize dictionaries to store options data
options_by_ticker = {}
price_error_by_ticker = []
call_options_data = {day: {} for day in fridays}
call_options_data_short = {}
stock_price = {}
# Set a breakpoint
# Iterate over each ticker
for ticker in lines:
    try:
        if len(ticker)<5:
        # Fetch the latest stock price for the ticker
            stock_price[ticker] = robin.get_latest_price(ticker)
            rm_row = []
            # Iterate over each expiration day
            if float(stock_price[ticker][0])>minPrice:
                for day in fridays:
                    # Fetch call options data for the ticker and expiration day
                    call_options = []
                    call_options = robin.find_options_by_expiration(ticker, str(day),optionType='call')
                    # Store call options data in the call_options_data dictionary
                    call_options_data[day][ticker] = call_options
                    strikePrice = []
                    bidPrice = []
                    diff = []
                    for option in call_options:
                        diff.append(float(option['strike_price']) - float(stock_price[ticker][0]))
        
                    # Find the indices of options with negative differences
                    rm_row = [i for i, val in enumerate(diff) if val < 0]
                    
                    # Create new lists containing only the options with positive differences
                    call_options_filtered = [call_options[i] for i in range(len(call_options)) if i not in rm_row]
                    diff_filtered = [diff[i] for i in range(len(diff)) if i not in rm_row]
                    
                    # Update call_options and diff with the filtered lists
                    call_options = call_options_filtered
                    diff = diff_filtered

                    # Get the sorted indices and values simultaneously
                    sorted_indices_and_values = sorted(enumerate(diff), key=lambda x: x[1])
                    
                    # Separate sorted indices and values
                    sorted_indices = [index for index, _ in sorted_indices_and_values]
                    sorted_values = [value for _, value in sorted_indices_and_values]
                    outFill = []
                    tempOption = []
                    if sorted_indices:  # Check if sorted_indices is not empty
                        tempOption = call_options[sorted_indices[0]]
                        outFill = [
                            ticker,
                            float(stock_price[ticker][0]),  # Convert to float
                            float(tempOption['strike_price']),
                            float(tempOption['bid_price']),
                            (100 * (float(tempOption['bid_price']) / float(tempOption['strike_price'])))  # Convert to float before division
                        ]
                        # Assuming day is a datetime.date object
                        day_str = str(day)  # Convert datetime.date to string
                        
                        # Append outFill to the list corresponding to the day
                        if day_str not in call_options_data_short:
                            call_options_data_short[day_str] = []  # Initialize list if it doesn't exist
                        call_options_data_short[day_str].append(outFill)

                                # print(f"Options data for ticker '{ticker}' processed successfully.")
    except Exception as e:
        # Handle errors and store the ticker in the price_error_by_ticker list
        price_error_by_ticker.append(ticker)
        print(f"Error processing ticker '{ticker}': {e}")

# Print the options data
print("Options data by ticker and expiration day:")
print(options_by_ticker)

# Print stock prices
print("Stock prices:")
print(stock_price)

# Print tickers that produced errors
print("Tickers with price errors:")
print(price_error_by_ticker)
#%%
out_sorted = {}
for day in call_options_data_short:
    day_str = str(day)  # Convert datetime.date to string
    
    # Append outFill to the list corresponding to the day
    if day_str not in out_sorted:
        out_sorted[day_str] = []  # Initialize list if it doesn't exist
    out_sorted[day_str] = sorted(call_options_data_short[day_str], key=lambda x: x[4],reverse=True)  # Sort in descending order
