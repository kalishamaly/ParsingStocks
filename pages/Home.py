#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  8 16:32:37 2025

@author: kalishamay
"""

import requests
from dash import html, callback, Output, Input, dash_table, register_page

register_page(__name__, path="/", name="Home", order=0)
  

layout = html.Div(children=[
    html.H1("Welcome to the stock loader"),
    
    html.B(html.H2("Current App Capabilities")),
    html.Div(children=[
        html.P("- List all SEC stock tickers")#,
        #html.P("- Read in all ticker price data and plot with duration options")
    ]),
    
    html.B(html.H2("Planned App Capabilities")),
    html.Div(children=[
        html.P("- Make a market status check page"),
        html.P("- Make a watch list page -----> Eventually write to google sheets"),
    ])
])