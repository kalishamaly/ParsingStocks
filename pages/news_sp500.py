#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 00:30:46 2025

@author: kalishamay
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S&P 500 (SPY) — Aggregated Ticker News
- Scrapes SPY constituents from Slickcharts
- Fetches Yahoo Finance news via yfinance.Ticker(...).news for each ticker
- Aggregates, de-dupes, sorts by time, optional keyword filter
- Renders as clean cards (uses your existing news CSS)
"""

import time
import re
from datetime import datetime, timezone
import requests
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
from dash import html, dcc, register_page, callback, Output, Input, State, no_update

register_page(__name__, path="/news/sp500", name="S&P 500 News", order=6)

# ----------------------- Helpers -----------------------

def get_spy_tickers():
    """
    Get S&P 500 tickers from Slickcharts (sorted by index weight).
    """
    url = "https://www.slickcharts.com/sp500"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; KaliBot/1.0; +github.com/shamalykali)"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for row in soup.select("table.table tbody tr"):
        tds = row.find_all("td")
        if len(tds) >= 3:
            t = tds[2].get_text(strip=True).replace(".", "-")
            out.append(t)
    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for t in out:
        if t not in seen:
            uniq.append(t)
            seen.add(t)
    return uniq

def clean_ticker(s: str) -> str:
    if not s:
        return ""
    return s.strip().upper().replace(" ", "").replace(".", "-")

def time_ago(ts: int | float | None) -> str:
    if not ts:
        return ""
    now = datetime.now(timezone.utc).timestamp()
    delta = max(0, int(now - int(ts)))
    minutes = delta // 60
    hours = minutes // 60
    days = hours // 24
    if delta < 60: return f"{delta}s ago"
    if minutes < 60: return f"{minutes}m ago"
    if hours < 24: return f"{hours}h ago"
    return f"{days}d ago"

def matches_keyword(item: dict, keyword: str) -> bool:
    if not keyword:
        return True
    k = keyword.lower().strip()
    title = (item.get("title") or "").lower()
    publisher = (item.get("publisher") or "").lower()
    # match in title or publisher; extend with summary if Yahoo provides it
    return (k in title) or (k in publisher)

def NewsCard(item: dict) -> html.Div:
    title = item.get("title") or "Untitled"
    link  = item.get("link") or "#"
    pub   = item.get("publisher") or item.get("provider") or "—"
    ts    = item.get("providerPublishTime")
    ago   = time_ago(ts)
    rel   = item.get("relatedTickers") or []
    thumb = None
    thumb_dict = item.get("thumbnail")
    if isinstance(thumb_dict, dict):
        for k in ("resolutions", "sizes", "thumbnails"):
            if k in thumb_dict and thumb_dict[k]:
                thumb = thumb_dict[k][0].get("url")
                break

    # main row: text + (optional) thumbnail
    return html.Div(
        className="news-card",
        children=[
            html.Div(className="news-row", children=[
                html.Div(className="news-meta", children=[
                    html.A(title, href=link, target="_blank", rel="noopener", className="news-title"),
                    html.Div(f"{pub} • {ago}", className="sub"),
                ]),
                html.Img(src=thumb, className="news-thumb") if thumb else None,
            ]),
            html.Div(
                "Related: " + ", ".join(rel) if rel else "",
                className="sub", style={"marginTop": "6px"}
            )
        ]
    )

def fetch_news_for_tickers(tickers, per_ticker=2, sleep_s=0.15, max_items=400, keyword=""):
    """
    Pull .news for each ticker with small delay to be gentle.
    Keep up to `per_ticker` items per ticker, dedupe by (title, link), sort by time desc.
    Optional keyword filter applied after aggregation.
    """
    seen_keys = set()
    all_items = []

    for i, t in enumerate(tickers):
        try:
            tk = yf.Ticker(t)
            news = tk.news or []
            kept_for_this = 0
            for n in news:
                key = (n.get("title"), n.get("link"))
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                n["sourceTicker"] = t
                all_items.append(n)
                kept_for_this += 1
                if kept_for_this >= int(per_ticker):
                    break
        except Exception:
            # skip ticker on error
            pass

        if len(all_items) >= max_items:
            break

        # small pause to avoid hammering
        time.sleep(sleep_s)

    # optional keyword filter
    if keyword:
        all_items = [x for x in all_items if matches_keyword(x, keyword)]

    # sort newest first
    all_items.sort(key=lambda x: x.get("providerPublishTime") or 0, reverse=True)

    return all_items

# ----------------------- Layout -----------------------

layout = html.Div(
    className="container",
    children=[
        html.Div(className="h1", children="📰 S&P 500 — Aggregated Ticker News"),
        html.Div(className="sub", children="Pulls headlines from Yahoo Finance for every SPY component; de-duped & sorted."),
        html.Div(className="sp-16"),

        html.Div(className="card", children=[
            html.Div(className="card-header", children=html.Div("Controls", className="card-title")),
            html.Div(className="card-body", children=[
                html.Div(style={
                    "display":"grid",
                    "gridTemplateColumns":"repeat(auto-fit, minmax(200px, 1fr))",
                    "gap":"10px",
                    "alignItems":"end"
                }, children=[
                    html.Div(children=[
                        html.Label("Scan top N tickers (by SPY weight)", className="sub"),
                        dcc.Dropdown(
                            id="spyN", clearable=False, value=75, style={"width":"100%"},
                            options=[{"label": str(n), "value": n} for n in (25, 50, 75, 100, 150, 250, 500)]
                        )
                    ]),
                    html.Div(children=[
                        html.Label("Headlines per ticker", className="sub"),
                        dcc.Dropdown(
                            id="perTicker", clearable=False, value=2, style={"width":"100%"},
                            options=[{"label": str(n), "value": n} for n in (1, 2, 3, 4, 5)]
                        )
                    ]),
                    html.Div(children=[
                        html.Label("Keyword (optional)", className="sub"),
                        dcc.Input(id="kw", type="text", placeholder="e.g., earnings, guidance, AI",
                                  debounce=True, style={"width":"100%"})
                    ]),
                    html.Div(children=[
                        html.Label("Max total items", className="sub"),
                        dcc.Dropdown(
                            id="maxItems", clearable=False, value=300, style={"width":"100%"},
                            options=[{"label": str(n), "value": n} for n in (150, 200, 300, 400, 600)]
                        )
                    ]),
                    html.Button("Fetch All", id="fetch_spy_news", className="btn btn-primary"),
                ]),
            ]),
            html.Div(id="spy_news_status", className="card-footer sub", children="Ready."),
        ]),

        html.Div(className="sp-16"),

        html.Div(className="card", children=[
            html.Div(className="card-header", children=[
                html.Div("Results", className="card-title"),
                html.Span(id="spy_news_summary", className="badge")
            ]),
            html.Div(className="card-body", children=[dcc.Loading(type="dot", children=html.Div(id="spy_news_grid"))]),
        ]),
    ],
)

# ----------------------- Callbacks -----------------------

@callback(
    Output("spy_news_grid", "children"),
    Output("spy_news_status", "children"),
    Output("spy_news_summary", "children"),
    Input("fetch_spy_news", "n_clicks"),
    State("spyN", "value"),
    State("perTicker", "value"),
    State("maxItems", "value"),
    State("kw", "value"),
    prevent_initial_call=True
)
def run_spy_aggregate(_, topN, per_ticker, max_items, kw):
    try:
        # 1) SPY constituents (sorted by weight, heavy names first)
        tickers = get_spy_tickers()
        if not tickers:
            return html.Div("Failed to load S&P 500 tickers.", className="sub"), "Error", "error"

        topN = int(topN or 75)
        per_ticker = int(per_ticker or 2)
        max_items = int(max_items or 300)
        tickers = tickers[:topN]

        # 2) Fetch headlines for each ticker, de-dupe, sort
        news = fetch_news_for_tickers(
            tickers=tickers,
            per_ticker=per_ticker,
            sleep_s=0.15,
            max_items=max_items,
            keyword=(kw or "").strip()
        )

        if not news:
            return html.Div("No headlines found.", className="sub"), "No news", "0 items"

        # 3) Render cards
        grid = html.Div(className="news-grid", children=[NewsCard(n) for n in news])

        status = f"Scanned {len(tickers)} tickers • Returned {len(news)} headlines"
        badge  = f"{len(news)} items"

        return grid, status, badge

    except Exception as e:
        return (
            html.Div([
                html.Div("Failed to fetch SPY news.", className="badge danger"),
                html.Pre(str(e), className="sub")
            ]),
            "Error",
            "error"
        )