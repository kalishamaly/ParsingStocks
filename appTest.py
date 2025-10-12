#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 18:25:50 2025

@author: kalishamay
"""

from dash import Dash, html, dcc, page_container

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.H1("Main App Layout"),
    dcc.Link("Home", href="/"),
    html.Hr(),
    page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)