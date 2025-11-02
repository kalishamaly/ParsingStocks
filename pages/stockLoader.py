# Import necessary libraries
import requests  # Used to fetch SEC ticker data
from dash import html, callback, Output, Input, dash_table, register_page, dcc, State
import yfinance as yf
import pandas as pd
from collections import OrderedDict
from dash import callback_context
import dash as dash

# ---------- Page registration ----------
register_page(__name__, path="/stockLoader", name="Stock Loader", order=1)

# ---------- Shared table style (uses your CSS variables) ----------
COMMON_TABLE_PROPS = dict(
    page_size=100,
    style_table={"overflowX": "auto", "height": "70vh"},
    style_header={
        "backgroundColor": "rgba(255,255,255,.04)",
        "border": "none",
        "fontWeight": "600",
    },
    style_data={
        "backgroundColor": "transparent",
        "border": "none",
        "color": "var(--text)",
    },
    style_cell={
        "padding": "10px 12px",
        "whiteSpace": "normal",
        "textAlign": "left",
        "fontFamily": "Inter, system-ui, sans-serif",
        "fontSize": "13px",
        "maxWidth": 260,
        "textOverflow": "ellipsis",
    },
)

def SectionHeader(title, subtitle=None, right=None):
    return html.Div(
        [
            html.Div(
                [html.Div(title, className="h1"), html.Div(subtitle, className="sub") if subtitle else None]
            ),
            right,
        ],
        style={
            "display": "flex",
            "alignItems": "flex-end",
            "justifyContent": "space-between",
            "gap": "14px",
            "marginBottom": "10px",
        },
    )

# ---------- Layout ----------
layout = html.Div(
    className="container",
    children=[
        SectionHeader(
            "📥 Load SEC Stock Tickers",
            "Pull the SEC universe, preview it, then enrich with prices & simple signals.",
            right=html.Span("beta", className="badge warn"),
        ),

        # Controls + Actions
        html.Div(
            className="card",
            children=[
                html.Div(className="card-header", children=[html.Div("Actions", className="card-title")]),
                html.Div(
                    className="card-body",
                    children=[
                        html.Div(
                            style={"display": "flex", "gap": "10px", "flexWrap": "wrap"},
                            children=[
                                html.Button("Load tickers from SEC", id="loadBtn", n_clicks=0, className="btn btn-primary"),
                                html.Button(
                                    "Enrich with price data",
                                    id="dataBtn",
                                    n_clicks=0,
                                    className="btn btn-ghost",
                                    style={"display": "none"},
                                ),
                                html.Span(
                                    "Tip: click Load first, then Enrich.",
                                    className="sub",
                                    style={"alignSelf": "center"},
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),

        html.Div(className="sp-16"),

        # Results card (table / messages)
        html.Div(
            className="card",
            children=[
                html.Div(
                    className="card-header",
                    children=[
                        html.Div("Results", className="card-title"),
                        html.Span(id="statusBadge", className="badge"),
                    ],
                ),
                html.Div(
                    className="card-body",
                    children=[
                        dcc.Loading(type="dot", children=html.Div(id="outputContainer")),
                    ],
                ),
            ],
        ),

        # Stores
        dcc.Store(id="tickerNames"),
        dcc.Store(id="tickerPrice"),
    ],
)

# ---------- Callback ----------
@callback(
    Output("loadBtn", "style"),
    Output("outputContainer", "children"),
    Output("dataBtn", "style"),
    Output("tickerNames", "data"),
    Output("tickerPrice", "data"),
    Input("loadBtn", "n_clicks"),
    Input("dataBtn", "n_clicks"),
    Input("tickerNames", "data"),
    prevent_initial_call=True,
)
def handle_all_stock_actions(load_clicks, data_clicks, tickers):
    ctx = callback_context
    triggered_id = ctx.triggered_id

    hide_load_btn = dash.no_update
    output = dash.no_update
    show_data_btn = dash.no_update
    ticker_list = dash.no_update
    ticker_price_data = dash.no_update

    if triggered_id == "loadBtn":
        # Step 1: Load tickers from SEC
        sec_url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            "User-Agent": "Kali Shamaly (shamalykali@gmail.com)",
            "Accept": "application/json",
            "Connection": "keep-alive",
        }

        try:
            res = requests.get(sec_url, headers=headers)
            res.raise_for_status()
            data = res.json()
            # Flatten dict to list and keep just what you need
            records = list(data.values())

            # Full ticker list if you need elsewhere
            tickersLong = [item.get("ticker", "") for item in records]

            # Preview first 50 for UI
            tickers = [{"Ticker": item.get("ticker", ""), "Title": item.get("title", "")} for item in records[:50]]

            table = dash_table.DataTable(
                data=tickers,
                columns=[{"name": col, "id": col} for col in ["Ticker", "Title"]],
                **COMMON_TABLE_PROPS,
            )

            hide_load_btn = {"display": "none"}
            show_data_btn = {"display": "inline-block"}
            output = html.Div(
                [
                    html.Div(className="sub", children=f"Showing 50 of {len(records)} companies from the SEC feed."),
                    html.Div(className="sp-12"),
                    html.Div(className="table-wrap", children=[table]),
                ]
            )
            ticker_list = tickers

        except Exception as e:
            output = html.Div(
                [
                    html.Div("Failed to load data", className="badge danger"),
                    html.Div(className="sp-8"),
                    html.Pre(str(e), className="sub"),
                ]
            )
            hide_load_btn = {"display": "inline-block"}
            show_data_btn = {"display": "none"}

    elif triggered_id == "dataBtn" and tickers:
        # Step 2: Enrich tickers with stock prices using yfinance
        for i, item in enumerate(tickers):
            listCount = 0
            ticker = item.get("Ticker", "")
            try:
                dataTemp = yf.Ticker(ticker)
                hist = dataTemp.history(period="1y")
                if hist.empty:
                    raise ValueError("No price history returned")

                currentPrice = round(float(hist["Close"].iloc[-1]), 2)
                high_52w = round(float(hist["High"].max()), 2)
                within_5 = currentPrice >= (high_52w * 0.95)

                volume = int(hist["Volume"].iloc[-1])
                avgVol = float(hist["Volume"].mean())

                # Safer access for info dict
                pe = None
                try:
                    pe = dataTemp.info.get("forwardPE")
                except Exception:
                    pe = None

                # Price change stats (simple means)
                try:
                    price_change = round(float(hist["Close"].diff().mean()), 2)
                    pct_change = round(float(hist["Close"].pct_change().mean() * 100), 2)
                except Exception:
                    price_change = "Not Available"
                    pct_change = "Not Available"

                # Assign fields
                item["Price"] = currentPrice
                item["52 Week High"] = high_52w
                item["Within 5%?"] = "Yes" if within_5 else "No"
                item["Volume"] = volume
                item["Average Volume"] = round(avgVol, 0)
                item["P/E Ratio"] = pe if pe is not None else "Not Available"
                item["Price Change"] = price_change
                item["Percent Change"] = pct_change

                # Scoring
                if isinstance(currentPrice, (int, float)) and isinstance(high_52w, (int, float)):
                    if currentPrice >= high_52w:
                        listCount += 2
                    if currentPrice >= high_52w * 0.95:
                        listCount += 1
                    if volume >= avgVol:
                        listCount += 2
                    if volume >= 100_000:
                        listCount += 1
                    if avgVol >= 100_000:
                        listCount += 1
                    if isinstance(price_change, (int, float)) and price_change > 0:
                        listCount += 1
                        if price_change > 0.25:
                            listCount += 1
                        if price_change > 0.5:
                            listCount += 1
                    if isinstance(pct_change, (int, float)) and pct_change > 0:
                        listCount += 1
                        if pct_change > 10:
                            listCount += 1

                item["Watch List Count"] = listCount

            except Exception:
                # Graceful fallbacks
                item["Price"] = "Not Available"
                item["52 Week High"] = "Not Available"
                item["Within 5%?"] = "Not Available"
                item["Volume"] = "Not Available"
                item["Average Volume"] = "Not Available"
                item["P/E Ratio"] = "Not Available"
                item["Price Change"] = "Not Available"
                item["Percent Change"] = "Not Available"
                item["Watch List Count"] = 0

        # Styled table
        columns = [
            "Ticker",
            "Title",
            "Price",
            "Watch List Count",
            "52 Week High",
            "Within 5%?",
            "Volume",
            "Average Volume",
            "Price Change",
            "Percent Change",
        ]

        table = dash_table.DataTable(
            data=tickers,
            columns=[{"name": col, "id": col} for col in columns],
            style_data_conditional=[
                # 52W High vs Price
                {
                    "if": {"filter_query": "{52 Week High} <= {Price}", "column_id": "52 Week High"},
                    "backgroundColor": "rgba(34,197,94,.12)",  # success
                    "color": "var(--text)",
                },
                {
                    "if": {"filter_query": "{52 Week High} > {Price}", "column_id": "52 Week High"},
                    "backgroundColor": "rgba(239,68,68,.12)",  # danger
                    "color": "var(--text)",
                },
                # Within 5%
                {
                    "if": {"filter_query": "{Within 5%?} = 'Yes'", "column_id": "Within 5%?"},
                    "backgroundColor": "rgba(34,197,94,.12)",
                    "color": "var(--text)",
                },
                {
                    "if": {"filter_query": "{Within 5%?} = 'No'", "column_id": "Within 5%?"},
                    "backgroundColor": "rgba(239,68,68,.12)",
                    "color": "var(--text)",
                },
                # Volume vs Avg
                {
                    "if": {"filter_query": "{Volume} >= {Average Volume}", "column_id": "Volume"},
                    "backgroundColor": "rgba(34,197,94,.12)",
                    "color": "var(--text)",
                },
                {
                    "if": {"filter_query": "{Volume} < {Average Volume}", "column_id": "Volume"},
                    "backgroundColor": "rgba(239,68,68,.12)",
                    "color": "var(--text)",
                },
                # Avg Vol threshold
                {
                    "if": {"filter_query": "{Average Volume} >= 100000", "column_id": "Average Volume"},
                    "backgroundColor": "rgba(34,197,94,.12)",
                    "color": "var(--text)",
                },
                {
                    "if": {"filter_query": "{Average Volume} < 100000", "column_id": "Average Volume"},
                    "backgroundColor": "rgba(245,158,11,.15)",  # warn
                    "color": "var(--text)",
                },
                # Price Change
                {
                    "if": {"filter_query": "{Price Change} >= 0", "column_id": "Price Change"},
                    "backgroundColor": "rgba(34,197,94,.12)",
                    "color": "var(--text)",
                },
                {
                    "if": {"filter_query": "{Price Change} < 0", "column_id": "Price Change"},
                    "backgroundColor": "rgba(239,68,68,.12)",
                    "color": "var(--text)",
                },
                # Percent Change
                {
                    "if": {"filter_query": "{Percent Change} > 10", "column_id": "Percent Change"},
                    "backgroundColor": "rgba(34,197,94,.12)",
                    "color": "var(--text)",
                },
                {
                    "if": {
                        "filter_query": "{Percent Change} >= 0 && {Percent Change} <= 10",
                        "column_id": "Percent Change",
                    },
                    "backgroundColor": "rgba(245,158,11,.15)",
                    "color": "var(--text)",
                },
                {
                    "if": {"filter_query": "{Percent Change} < 0", "column_id": "Percent Change"},
                    "backgroundColor": "rgba(239,68,68,.12)",
                    "color": "var(--text)",
                },
            ],
            **COMMON_TABLE_PROPS,
        )

        output = html.Div(
            [
                html.Div(
                    className="sub",
                    children="Enriched with 1-year price history (Close/High/Volume) and quick flags.",
                ),
                html.Div(className="sp-12"),
                html.Div(className="table-wrap", children=[table]),
            ]
        )
        ticker_price_data = tickers

    return hide_load_btn, output, show_data_btn, ticker_list, ticker_price_data


