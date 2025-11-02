#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 18:44:20 2025

@author: kalishamay
"""

import yfinance as yf
import requests
import plotly.graph_objs as go
from datetime import datetime, timedelta
from dash import Dash, html, dcc, callback, Output, Input, dash_table, page_container
import os
import gunicorn
from dash import no_update

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
app.title = "ParsingStocks"
server = app.server

app.layout = html.Div([
    dcc.Location(id="url"),
    
    html.Div(className="container", children=[
        
        # Header Banner
        html.Header(className="app-header", children=[
            html.Div(className="brand", children=[
                html.Div("📊 ParsingStocks", className="h1"),
                html.Div("A lightweight toolkit for loading tickers, breadth, and news", className="sub")
            ]),
            html.Div(className="header-actions", children=[
                html.Span("beta", className="badge warn")
            ])
        ]),

        # Navigation Bar (clean + spaced) — updated links
        # Navigation Bar (clean + spaced) — with IDs for active class
        html.Nav(id="top-nav", className="top-nav", children=[
            dcc.Link("Home", href="/",                 id="nav-home",   className="nav-item"),
            dcc.Link("Stock Loader", href="/stockLoader",           id="nav-loader", className="nav-item"),
            dcc.Link("SPY Breadth",  href="/marketCheck/spyCheck",  id="nav-spy",    className="nav-item"),
            dcc.Link("R3000 Breadth",href="/marketCheck/russell3000", id="nav-r3k",  className="nav-item"),
            dcc.Link("Ticker News",  href="/news",                   id="nav-news",  className="nav-item"),
            dcc.Link("S&P 500 News", href="/news/sp500",             id="nav-sp500", className="nav-item"),
        ]),

        html.Div(className="sp-16"),

        # Main Page Content
        html.Div(className="card", children=[
            html.Div(className="card-body", children=page_container)
        ]),

        html.Div(className="sp-24"),

        # Footer
        html.Footer(className="footer sub", children=[
            "Built with Dash • ",
            html.Span("v0.1", className="badge")
        ]),
    ]),

    # Hidden Stores (keep exactly as-is)
    html.Button(id="loadBtn", style={"display": "none"}),
    html.Button(id="dataBtn", style={"display": "none"}),
    html.Div(id="outputContainer", style={"display": "none"}),
    dcc.Store(id="tickerNames"),
    dcc.Store(id="tickerPrice"),
])


@callback(
    Output("nav-home",  "className"),
    Output("nav-loader","className"),
    Output("nav-spy",   "className"),
    Output("nav-r3k",   "className"),
    Output("nav-news",  "className"),
    Output("nav-sp500", "className"),
    Input("url", "pathname"),
)
def set_active_nav(path):
    base = "nav-item"
    active = "nav-item active"
    # map simple prefixes
    return (
        active if path == "/" else base,
        active if path.startswith("/stockLoader") else base,
        active if path.startswith("/marketCheck/spyCheck") else base,
        active if path.startswith("/marketCheck/russell3000") else base,
        active if path == "/news" else base,
        active if path.startswith("/news/sp500") else base,
    )
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
