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
import gunicorn

app = Dash(__name__, use_pages=True)
server = app.server 

app.layout = html.Div([
    html.H1("📊 Stock App"),
    dcc.Link("Home", href="/"), html.Br(),
    dcc.Link("Stock Loader", href="/stockLoader"), html.Br(),
    # dcc.Link("Watch List", href = "/watchList"), html.Br(),
    html.Hr(),
    page_container
])


# this works 
# if __name__ == "__main__":
#     app.run_server(
#         debug=True,       # Enables hot-reload and error messages
#         host="127.0.0.1", # Default: local machine only (use "0.0.0.0" for all devices on LAN)
#         port=8050         # Default port, change if you want e.g. 8051
#     )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)