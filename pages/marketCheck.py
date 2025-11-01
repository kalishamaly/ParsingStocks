#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 11 23:17:59 2025

@author: kalishamay
"""

import requests  # Used to fetch SEC ticker data
from dash import html, callback, Output, Input, dash_table, register_page, dcc  # Dash components for building the app
import yfinance as yf  # Used for fetching historical stock data (commented-out portion)
from dash import Dash, dash_table
import pandas as pd
from collections import OrderedDict

register_page(__name__, path="/marketCheck", name="Market Status Check", order=2)
  

layout = html.Div(children=[
    html.H2("📥 Market Status Check", style={'textAlign': 'center'}),
    html.Div([
        dcc.Link("SPY Market Check", href="/marketCheck/spyCheck"),
        html.Br(),
        dcc.Link("Russell 3000 Market Check", href="/marketCheck/russell3000"),
        html.Br(),
    ], style={'textAlign': 'center', 'marginTop': '20px'})],
    
)