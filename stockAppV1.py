#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 18:44:20 2025

@author: kalishamay
"""

import yfinance as yf
import requests
import plotly.graph_objs as go
#import pandas as pd
from datetime import datetime, timedelta
import pdb
from dash import Dash, html, dcc, callback, Output, Input, dash_table, page_container
import os

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.H1("📊 Stock App"),
    dcc.Link("Home", href="/"), html.Br(),
    dcc.Link("Stock Loader", href="/stockLoader"), html.Br(),
    # dcc.Link("Watch List", href = "/watchList"), html.Br(),
    html.Hr(),
    page_container
])

# if __name__ == "__main__":
#     app.run_server(debug=True)

# if __name__ == "__main__":
#     # bind to the env PORT if provided by the host, otherwise 8050 locally
#     app.run_server(host="0.0.0.0", debug=True)
    
    
if __name__ == "__main__":
    app.run_server(
        debug=True,       # Enables hot-reload and error messages
        host="127.0.0.1", # Default: local machine only (use "0.0.0.0" for all devices on LAN)
        port=8050         # Default port, change if you want e.g. 8051
    )