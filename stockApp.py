#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  8 20:15:45 2025

@author: kalishamay
"""

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from alpha_vantage.timeseries import TimeSeries
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Define the path to the file containing ticker symbols
file_path = "/Users/kalishamaly/Downloads/all_tickers.txt"

# Define the second Friday date
today = datetime.today()

with open(file_path, "r") as file:
    # Read the contents of the file
    content = file.read()

    # Split the content into lines
    lines = content.splitlines()  # or lines = content.split('\n')
    lines = [line for line in lines if len(line) <= 4]

dropdown_options = [{'label': line, 'value': line} for line in lines]

# Alpha Vantage API Key (You must replace 'YOUR_API_KEY' with your actual key)
API_KEY = 'XP3MPGVQYQF02X54'

# Initialize Dash app
app = dash.Dash()

# Layout of the app
app.layout = html.Div([
    dcc.Dropdown(
        id='demo-dropdown',
        options=dropdown_options,  # Providing the options to the dropdown
        value=lines[0]  # Default value (first ticker symbol)
    ),
    html.Div(id='dd-output-container'),  # This will display the stock price
    dcc.Graph(id='stock-graph')  # This will display the plot
])

# Define the callback function
@app.callback(
    [Output('dd-output-container', 'children'),  # The output container ID should be a string
     Output('stock-graph', 'figure')],  # Output for the graph
    Input('demo-dropdown', 'value')  # The dropdown ID should also be a string
)
def update_output(value):
    try:
        # Create an instance of the Alpha Vantage TimeSeries class
        ts = TimeSeries(key=API_KEY, output_format='pandas')
        
        # Fetch the stock data (Intraday data with a 1-minute interval)
        data, meta_data = ts.get_daily(symbol=value, outputsize='compact')  # 'compact' returns the last 100 days
        intraDay, intraMeta = ts.get_intraday(symbol=value, interval='1min', outputsize='full')

        # Check if data is available
        if data.empty:
            return f"No data available for {value}. Please check the ticker symbol.", {}

        # Extract the most recent closing price
        stock_price = data['4. close'].iloc[0]  # '4. close' corresponds to the closing price

        # Calculate Simple Moving Average (SMA) for 20 and 50 days
        data['SMA20'] = data['4. close'].rolling(window=20).mean()
        data['SMA50'] = data['4. close'].rolling(window=50).mean()

        # Calculate Bollinger Bands
        data['20-day_std'] = data['4. close'].rolling(window=20).std()
        data['UpperBand'] = data['SMA20'] + (data['20-day_std'] * 2)
        data['LowerBand'] = data['SMA20'] - (data['20-day_std'] * 2)

        # Create a candlestick chart
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['1. open'],
            high=data['2. high'],
            low=data['3. low'],
            close=data['4. close'],
            name='Candlesticks',
            increasing_line_color='green',
            decreasing_line_color='red',
        ))

        # Add SMA20 and SMA50 lines
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA20'],
            mode='lines',
            name='SMA 20',
            line=dict(color='blue', width=2, dash='dash')
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA50'],
            mode='lines',
            name='SMA 50',
            line=dict(color='orange', width=2, dash='dash')
        ))

        # Add Bollinger Bands
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['UpperBand'],
            mode='lines',
            name='Upper Bollinger Band',
            line=dict(color='purple', width=1, dash='dot')
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['LowerBand'],
            mode='lines',
            name='Lower Bollinger Band',
            line=dict(color='purple', width=1, dash='dot')
        ))

        # Update layout with additional features
        fig.update_layout(
            title=f'{value} Stock Price with Technical Indicators',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            template='plotly_dark',  # Use Plotly's dark theme
            plot_bgcolor='rgb(12, 12, 12)',  # Dark background for the plot area
            xaxis_rangeslider_visible=False,  # Hide range slider at the bottom
            hovermode='x unified',  # Unified hover text across the chart
            height=700,
            showlegend=True
        )

        # Add annotations to the plot (e.g., marking the highest price of the day)
        highest_point = data['4. close'].idxmax()
        highest_value = data['4. close'].max()

        fig.add_annotation(
            x=highest_point,
            y=highest_value,
            text=f"Highest Price: ${highest_value:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            ax=0,
            ay=-50,
            font=dict(color='white')
        )

        # Return the stock price and the plot
        return f'You have selected {value}. The current stock price is ${stock_price:.2f}', fig
    
    except Exception as e:
        return f"An error occurred: {e}", {}

if __name__ == '__main__':
    app.run_server(debug=True)
