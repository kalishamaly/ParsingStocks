#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 00:15:40 2025

@author: kalishamay
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Russell 3000 Breadth — BAR CHARTS (2 rows, shared X, unified hover, synced cursor line)
Row 1: % ≥ SMA(window) and % within ±5% of SMA(window)
Row 2: IWV Close (proxy for Russell 3000)
"""

import math, time, requests, yfinance as yf, pandas as pd
from bs4 import BeautifulSoup
from dash import html, dcc, register_page, callback, Output, Input
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Register page
register_page(__name__, path="/marketCheck/russell3000", name="Market Status Check — Russell 3000", order=1)

# ---------- UI ----------
def SectionHeader(title, subtitle=None, right=None):
    return html.Div(
        [html.Div([html.Div(title, className="h1"),
                   html.Div(subtitle, className="sub") if subtitle else None]),
         right],
        style={"display":"flex","alignItems":"flex-end","justifyContent":"space-between","marginBottom":"10px"}
    )

# ---------- Helpers ----------
import re
from urllib.parse import urljoin

def get_r3k_tickers():
    """
    Get Russell 3000 tickers via IWV (iShares Russell 3000 ETF) holdings CSV.
    We first fetch the IWV page, discover the CSV holdings link in the HTML,
    then download + parse. This avoids the Slickcharts 404.
    """
    base = "https://www.ishares.com"
    fund_url = "https://www.ishares.com/us/products/239714/ishares-russell-3000-etf"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; KaliBot/1.0; +github.com/shamalykali)"
    }

    # Step 1 — fetch the fund page and locate a CSV holdings link
    r = requests.get(fund_url, headers=headers, timeout=30)
    r.raise_for_status()
    html = r.text

    # Look for either legacy `.ajax?fileType=csv` pattern or newer `downloadFile?fileType=csv`
    m = re.search(r'href="([^"]+(?:\.ajax|downloadFile)\?[^"]*fileType=csv[^"]*)"', html, re.IGNORECASE)
    if not m:
        # Some pages lazy-load; try BlackRock mirror as a backup source of the same content
        mirror = "https://www.blackrock.com/us/individual/products/239714/ishares-russell-3000-etf"
        r2 = requests.get(mirror, headers=headers, timeout=30)
        r2.raise_for_status()
        m = re.search(r'href="([^"]+(?:\.ajax|downloadFile)\?[^"]*fileType=csv[^"]*)"', r2.text, re.IGNORECASE)
        if not m:
            raise RuntimeError("Could not locate IWV holdings CSV link on iShares/BlackRock pages")

    csv_url = m.group(1)
    if csv_url.startswith("/"):
        csv_url = urljoin(base, csv_url)
    elif csv_url.startswith("http") is False:
        csv_url = urljoin(fund_url, csv_url)

    # Step 2 — download the CSV
    csv_resp = requests.get(csv_url, headers=headers, timeout=60)
    csv_resp.raise_for_status()
    content = csv_resp.text

    # Step 3 — detect header row dynamically (iShares often adds 9–11 intro lines)
    # Find the first line that looks like a header with a "Ticker" (or similar) column
    lines = content.splitlines()
    header_idx = None
    for i, line in enumerate(lines[:50]):  # scan first ~50 lines
        low = line.lower()
        if ("ticker" in low) or ("ticker symbol" in low) or ("sedol" in low and "name" in low):
            header_idx = i
            break
    if header_idx is None:
        # Fall back to common offset of 9–11 lines before the real table
        header_idx = 9

    import io
    df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])))
    # Normalize possible column name variants
    cols_lower = {c.lower(): c for c in df.columns}
    ticker_col = None
    for cand in ("ticker", "ticker symbol", "symbol", "holding ticker"):
        if cand in cols_lower:
            ticker_col = cols_lower[cand]
            break
    if ticker_col is None:
        # Some files nest a 'Ticker' without exact match; try fuzzy pick
        for c in df.columns:
            if "tick" in c.lower():
                ticker_col = c
                break
    if ticker_col is None:
        raise RuntimeError("IWV CSV parsed, but no Ticker column found")

    # Clean and dedupe
    tickers = (
        df[ticker_col]
        .dropna()
        .astype(str)
        .str.strip()
        .str.replace(".", "-", regex=False)   # align with yfinance's BRK.B -> BRK-B style
        .tolist()
    )

    seen = set()
    uniq = []
    for t in tickers:
        if t and t not in seen:
            uniq.append(t)
            seen.add(t)

    # IWV often carries ~2,500–2,700 names (free-float & sampling). That’s fine for breadth.
    return uniq

def unit_to_days(n, unit):
    if n is None: return None
    u = str(unit).upper(); n = float(n)
    return {"D": int(n), "W": int(n*5), "M": int(n*21), "Y": int(n*252)}.get(u, None)

def drop_tz(df):
    if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
        df = df.tz_convert("UTC").tz_localize(None)
    return df

def safe_close(dl: pd.DataFrame) -> pd.DataFrame:
    """
    Robustly extract close-price matrix from yfinance.download output.
    Handles (field, ticker) or (ticker, field) MultiIndex and single-index.
    Falls back to 'Adj Close' if 'Close' is absent.
    """
    if dl is None or dl.empty: return pd.DataFrame()
    cols = dl.columns

    def _xs(level_idx, field):
        out = dl.xs(field, axis=1, level=level_idx, drop_level=True).copy()
        out.columns = [str(c) for c in out.columns]
        return out

    if isinstance(cols, pd.MultiIndex):
        lv0 = set(cols.get_level_values(0)); lv1 = set(cols.get_level_values(1))
        if "Close" in lv0:     return _xs(0, "Close")
        if "Adj Close" in lv0: return _xs(0, "Adj Close")
        if "Close" in lv1:     return _xs(1, "Close")
        if "Adj Close" in lv1: return _xs(1, "Adj Close")
        close_cols = [c for c in cols if any(k in c for k in ("Close", "Adj Close"))]
        if close_cols:
            out = dl.loc[:, close_cols].copy(); new_cols = []
            for c in out.columns:
                if isinstance(c, tuple):
                    if c[0] in ("Close","Adj Close"): new_cols.append(str(c[1]))
                    elif c[1] in ("Close","Adj Close"): new_cols.append(str(c[0]))
                    else: new_cols.append("-".join(map(str,c)))
                else: new_cols.append(str(c))
            out.columns = new_cols; return out
        raise ValueError("Could not find Close/Adj Close in columns.")
    # Single-index
    if "Close" in dl.columns:
        out = dl[["Close"]].copy(); out.columns = ["SINGLE"]; return out
    if "Adj Close" in dl.columns:
        out = dl[["Adj Close"]].copy(); out.columns = ["SINGLE"]; return out
    raise ValueError("No Close/Adj Close in columns (single-index).")

def batch_download(tickers, period_str, batch=150, pause=0.5):
    """
    Download in batches to avoid thread/resource limits.
    threads=False; small pause between batches.
    """
    frames = []
    for i in range(0, len(tickers), batch):
        chunk = tickers[i:i+batch]
        dl = yf.download(" ".join(chunk), period=period_str, group_by="ticker",
                         auto_adjust=False, threads=False, progress=False)
        close = safe_close(dl); close = drop_tz(close)
        close.columns = [str(c).split()[0] for c in close.columns]
        frames.append(close); time.sleep(pause)
    if not frames: return pd.DataFrame()
    out = pd.concat(frames, axis=1, join="outer")
    return out.loc[:, ~out.columns.duplicated()].sort_index()

def fetch_index_proxy(period_str) -> pd.Series:
    """
    IWV = iShares Russell 3000 ETF
    """
    dl = yf.download("IWV", period=period_str, auto_adjust=False, threads=False, progress=False)
    close_df = safe_close(dl); close_df = drop_tz(close_df)
    s = close_df.iloc[:, 0]; s.name = "IWV"
    return s

# ---------- Layout ----------
layout = html.Div(
    className="container",
    children=[
        SectionHeader(
            "📊 Russell 3000 Breadth — Bar Charts",
            "Row 1: breadth bars • Row 2: IWV close bars • Shared X, unified hover, synced cursor line",
            right=html.Span("beta", className="badge warn"),
        ),

        html.Div(className="card", children=[
            html.Div(className="card-header", children=[html.Div("Parameters", className="card-title")]),
            html.Div(className="card-body", children=[
                html.Div(style={
                    "display":"grid",
                    "gridTemplateColumns":"repeat(auto-fit, minmax(220px, 1fr))",
                    "gap":"10px",
                    "alignItems":"start",
                }, children=[
                    dcc.Input(id="num1", type="number", min=1, value=180, step="any", style={"width":"100%"}),
                    dcc.Dropdown(id="unit1",
                        options=[{"label":"Days","value":"D"},{"label":"Weeks","value":"W"},
                                 {"label":"Months","value":"M"},{"label":"Years","value":"Y"}],
                        value="D", clearable=False, style={"width":"100%","zIndex":1500}),
                    dcc.Input(id="num2", type="number", min=1, value=5, step="any", style={"width":"100%"}),
                    dcc.Dropdown(id="unit2",
                        options=[{"label":"Days","value":"D"},{"label":"Weeks","value":"W"},
                                 {"label":"Months","value":"M"},{"label":"Years","value":"Y"}],
                        value="D", clearable=False, style={"width":"100%","zIndex":1500}),
                ]),
            ]),
            html.Div(className="card-footer", children=[
                html.Button("Run Check", id="checkBtn_r3k", className="btn btn-primary"),
                html.Div(id="runStatus_r3k", className="sub", style={"marginLeft":"8px"})
            ]),
        ]),

        html.Div(className="sp-16"),

        html.Div(className="card", children=[
            html.Div(className="card-header", children=[
                html.Div("Results", className="card-title"),
                html.Span(id="summaryBadge_r3k", className="badge")
            ]),
            html.Div(className="card-body", children=[dcc.Loading(type="dot", children=html.Div(id="r3k_body"))]),
        ]),
    ],
)

# ---------- Callback ----------
@callback(
    Output("r3k_body","children"),
    Output("runStatus_r3k","children"),
    Output("summaryBadge_r3k","children"),
    Input("checkBtn_r3k","n_clicks"),
    Input("num1","value"), Input("unit1","value"),
    Input("num2","value"), Input("unit2","value"),
    prevent_initial_call=True
)
def r3k_check(_, num1, unit1, num2, unit2):
    # Inputs
    window_days = unit_to_days(num1, unit1)
    interval = unit_to_days(num2, unit2) or 1
    if not window_days or window_days <= 0:
        return html.Div("Enter a valid window.", className="sub"), "Invalid parameters", "error"

    # SMA window: use min(window_days, 100)
    sma_window = max(1, min(window_days, 100))

    # Data
    tickers = get_r3k_tickers()
    if not tickers:
        return html.Div("No tickers scraped for Russell 3000.", className="sub"), "Error", "error"

    lookback = window_days + sma_window + 20
    period_str = f"{min(lookback,1000)}d" if lookback <= 1000 else "max"

    close = batch_download(tickers, period_str=period_str, batch=150, pause=0.5)
    if close.empty:
        return html.Div("No price data returned.", className="sub"), "Error", "error"

    close = close.dropna(how="all")
    sma = close.rolling(sma_window).mean()
    close_win = close.tail(window_days)
    sma_win = sma.reindex_like(close_win)

    # Breadth
    above = (close_win >= sma_win)
    near  = (close_win >= 0.95*sma_win) & (close_win <= 1.05*sma_win)
    pct_above = (above.sum(axis=1) / above.count(axis=1) * 100.0).round(2)
    pct_near  = (near.sum(axis=1)  / near.count(axis=1) * 100.0).round(2)

    # Downsample for plotting density
    if interval > 1:
        pct_above = pct_above.iloc[::interval]
        pct_near  = pct_near.iloc[::interval]

    # IWV proxy
    iwv = fetch_index_proxy(period_str).reindex(pct_above.index, method="ffill")

    latest = float(pct_above.dropna().iloc[-1])

    # ---------- Plot: 2 rows of BAR charts ----------
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.10,
        subplot_titles=("Breadth vs SMA (Bars)", "IWV Close (Bars)")
    )

    # Row 1: Grouped bars (breadth)
    fig.add_trace(go.Bar(x=pct_above.index, y=pct_above.values,
                         name=f"≥ SMA{sma_window} (%)", marker=dict(opacity=0.9)), row=1, col=1)
    fig.add_trace(go.Bar(x=pct_near.index, y=pct_near.values,
                         name=f"Within ±5% SMA{sma_window} (%)", marker=dict(opacity=0.65)), row=1, col=1)

    # 50% reference line
    fig.add_hline(y=50, line_width=1, line_dash="dash",
                  line_color="rgba(127,127,127,0.5)", row=1, col=1)

    # Row 2: IWV close bars
    fig.add_trace(go.Bar(x=iwv.index, y=iwv.values, name="IWV Close", marker=dict(opacity=0.85)),
                  row=2, col=1)

    # Layout / aesthetics
    fig.update_layout(
        barmode="group",
        height=780,
        margin=dict(l=20, r=20, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="left", x=0),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="rgba(0,0,0,0.6)", font_size=12, namelength=-1),
    )

    # Synchronized cursor-following vertical line on BOTH rows
    for r in (1, 2):
        fig.update_xaxes(
            showspikes=True, spikemode="across", spikesnap="cursor",
            spikethickness=1.5, spikecolor="rgba(150,180,255,0.9)",
            spikedash="solid", row=r, col=1
        )

    # Axes cosmetics
    fig.update_yaxes(title_text="% of R3000 symbols", rangemode="tozero",
                     gridcolor="rgba(255,255,255,0.08)", zeroline=False, row=1, col=1)
    fig.update_yaxes(title_text="IWV Close", gridcolor="rgba(255,255,255,0.08)",
                     zeroline=False, row=2, col=1)

    # Shared range slider on bottom subplot
    fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.06), row=2, col=1)

    status = f"Universe≈{above.count(axis=1).iloc[-1]} • Window={window_days}d • SMA={sma_window} • Interval={interval}d"
    badge  = f"{latest:.1f}% ≥ SMA{sma_window}"

    return dcc.Graph(figure=fig, config={"displayModeBar": True}), status, badge