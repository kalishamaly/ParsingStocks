#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 11 23:17:59 2025

@author: kalishamay
"""

from dash import html, dcc, register_page

register_page(__name__, path="/marketCheck", name="Market Status Check", order=2)

def SectionHeader(title, subtitle=None, right=None):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(title, className="h1"),
                    html.Div(subtitle, className="sub") if subtitle else None
                ]
            ),
            right,
        ],
        style={
            "display": "flex",
            "alignItems": "flex-end",
            "justifyContent": "space-between",
            "gap": "14px",
            "marginBottom": "12px",
        },
    )

layout = html.Div(
    className="container",
    children=[
        SectionHeader(
            "📊 Market Status Check",
            "Choose a module to view market condition snapshots.",
            right=html.Span("beta", className="badge warn"),
        ),

        html.Div(className="card", children=[
            html.Div(className="card-header", children=[html.Div("Modules", className="card-title")]),

            html.Div(className="card-body", children=[
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(240px, 1fr))",
                        "gap": "14px",
                    },
                    children=[
                        dcc.Link(
                            href="/marketCheck/spyCheck",
                            className="nav-link",
                            children=html.Div(
                                style={
                                    "background": "var(--panel-2)",
                                    "borderRadius": "14px",
                                    "padding": "18px",
                                    "cursor": "pointer",
                                },
                                children=[
                                    html.Div("SPY Market Check", className="h2"),
                                    html.Div("S&P 500 based market condition scan.", className="sub"),
                                ],
                            )
                        ),
                        dcc.Link(
                            href="/marketCheck/russell3000",
                            className="nav-link",
                            children=html.Div(
                                style={
                                    "background": "var(--panel-2)",
                                    "borderRadius": "14px",
                                    "padding": "18px",
                                    "cursor": "pointer",
                                },
                                children=[
                                    html.Div("Russell 3000 Market Check", className="h2"),
                                    html.Div("Small + large cap breadth indicator.", className="sub"),
                                ],
                            )
                        ),
                    ]
                ),

                html.Div(className="sp-16"),
                html.Div(className="sub", children="Tip: Add more scan modules here over time (NASDAQ, sectors, etc.).")
            ]),
        ]),
    ],
)