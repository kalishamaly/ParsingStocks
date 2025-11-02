#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPY Market Breadth — BAR CHARTS (2 rows, shared X, unified hover, synced cursor line)
Row 1: Bars for % ≥ SMA(window) and % within ±5% of SMA(window)
Row 2: Bars for SPY Close
"""

import math, time, requests, yfinance as yf, pandas as pd
from bs4 import BeautifulSoup
from dash import html, dcc, register_page, callback, Output, Input
import plotly.graph_objects as go
from plotly.subplots import make_subplots

register_page(__name__, path="/marketCheck/spyCheck", name="Market Status Check Based on SPY", order=0)

# ---------- UI ----------
def SectionHeader(title, subtitle=None, right=None):
    return html.Div(
        [html.Div([html.Div(title, className="h1"),
                   html.Div(subtitle, className="sub") if subtitle else None]),
         right],
        style={"display":"flex","alignItems":"flex-end","justifyContent":"space-between","marginBottom":"10px"}
    )

# ---------- Helpers ----------
def get_spy_tickers():
    url = "https://www.slickcharts.com/sp500"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; KaliBot/1.0; +github.com/shamalykali)"}
    r = requests.get(url, headers=headers, timeout=20); r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    return [tr.find_all("td")[2].get_text(strip=True).replace(".","-")
            for tr in soup.select("table.table tbody tr") if len(tr.find_all("td"))>=3]

def unit_to_days(n, unit):
    if n is None: return None
    u = str(unit).upper(); n = float(n)
    return {"D": int(n), "W": int(n*5), "M": int(n*21), "Y": int(n*252)}.get(u, None)

def drop_tz(df):
    if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
        df = df.tz_convert("UTC").tz_localize(None)
    return df

def safe_close(dl: pd.DataFrame) -> pd.DataFrame:
    if dl is None or dl.empty: return pd.DataFrame()
    cols = dl.columns
    def _xs(level_idx, field): 
        out = dl.xs(field, axis=1, level=level_idx, drop_level=True).copy()
        out.columns = [str(c) for c in out.columns]; return out
    if isinstance(cols, pd.MultiIndex):
        lv0, lv1 = set(cols.get_level_values(0)), set(cols.get_level_values(1))
        if "Close" in lv0: return _xs(0,"Close")
        if "Adj Close" in lv0: return _xs(0,"Adj Close")
        if "Close" in lv1: return _xs(1,"Close")
        if "Adj Close" in lv1: return _xs(1,"Adj Close")
        close_cols = [c for c in cols if any(k in c for k in ("Close","Adj Close"))]
        if close_cols:
            out = dl.loc[:, close_cols].copy(); new_cols=[]
            for c in out.columns:
                if isinstance(c, tuple):
                    if c[0] in ("Close","Adj Close"): new_cols.append(str(c[1]))
                    elif c[1] in ("Close","Adj Close"): new_cols.append(str(c[0]))
                    else: new_cols.append("-".join(map(str,c)))
                else: new_cols.append(str(c))
            out.columns = new_cols; return out
        raise ValueError("Could not find Close/Adj Close in columns.")
    if "Close" in dl.columns:
        out = dl[["Close"]].copy(); out.columns=["SINGLE"]; return out
    if "Adj Close" in dl.columns:
        out = dl[["Adj Close"]].copy(); out.columns=["SINGLE"]; return out
    raise ValueError("No Close/Adj Close in columns (single-index).")

def batch_download(tickers, period_str, batch=100, pause=0.6):
    frames=[]
    for i in range(0,len(tickers),batch):
        chunk = tickers[i:i+batch]
        dl = yf.download(" ".join(chunk), period=period_str, group_by="ticker",
                         auto_adjust=False, threads=False, progress=False)
        close = safe_close(dl); close = drop_tz(close)
        close.columns = [str(c).split()[0] for c in close.columns]
        frames.append(close); time.sleep(pause)
    if not frames: return pd.DataFrame()
    out = pd.concat(frames, axis=1, join="outer")
    return out.loc[:, ~out.columns.duplicated()].sort_index()

def fetch_spy_close(period_str) -> pd.Series:
    dl = yf.download("SPY", period=period_str, auto_adjust=False, threads=False, progress=False)
    close_df = safe_close(dl); close_df = drop_tz(close_df)
    s = close_df.iloc[:,0]; s.name="SPY"; return s

# ---------- Layout ----------
layout = html.Div(
    className="container",
    children=[
        SectionHeader(
            "📊 SPY Breadth Check — Bar Charts",
            "Row 1: breadth bars • Row 2: SPY close bars • Shared X, unified hover, synced cursor line",
            right=html.Span("beta", className="badge warn"),
        ),
        html.Div(className="card", children=[
            html.Div(className="card-header", children=[html.Div("Parameters", className="card-title")]),
            html.Div(className="card-body", children=[
                html.Div(style={
                    "display":"grid","gridTemplateColumns":"repeat(auto-fit, minmax(220px, 1fr))",
                    "gap":"10px","alignItems":"start"
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
                html.Button("Run Check", id="checkBtn", className="btn btn-primary"),
                html.Div(id="runStatus", className="sub", style={"marginLeft":"8px"})
            ]),
        ]),
        html.Div(className="sp-16"),
        html.Div(className="card", children=[
            html.Div(className="card-header", children=[html.Div("Results", className="card-title"),
                                                        html.Span(id="summaryBadge", className="badge")]),
            html.Div(className="card-body", children=[dcc.Loading(type="dot", children=html.Div(id="spyCheck"))]),
        ]),
    ],
)

# ---------- Callback ----------
@callback(
    Output("spyCheck","children"),
    Output("runStatus","children"),
    Output("summaryBadge","children"),
    Input("checkBtn","n_clicks"),
    Input("num1","value"), Input("unit1","value"),
    Input("num2","value"), Input("unit2","value"),
    prevent_initial_call=True
)
def spy_check(_, num1, unit1, num2, unit2):
    # Inputs
    window_days = unit_to_days(num1, unit1)
    interval = unit_to_days(num2, unit2) or 1
    if not window_days or window_days <= 0:
        return html.Div("Enter a valid window.", className="sub"), "Invalid parameters", "error"
    sma_window = max(1, min(window_days, 100))

    # Data
    tickers = get_spy_tickers()
    lookback = window_days + sma_window + 20
    period_str = f"{min(lookback,1000)}d" if lookback <= 1000 else "max"

    close = batch_download(tickers, period_str=period_str, batch=100, pause=0.6)
    if close.empty:
        return html.Div("No price data returned.", className="sub"), "Error", "error"

    close = close.dropna(how="all")
    sma = close.rolling(sma_window).mean()
    close_win = close.tail(window_days)
    sma_win = sma.reindex_like(close_win)

    # Breadth metrics
    above = (close_win >= sma_win)
    near  = (close_win >= 0.95*sma_win) & (close_win <= 1.05*sma_win)
    pct_above = (above.sum(axis=1) / above.count(axis=1) * 100.0).round(2)
    pct_near  = (near.sum(axis=1)  / near.count(axis=1) * 100.0).round(2)

    # Downsample for plotting density
    if interval > 1:
        pct_above = pct_above.iloc[::interval]
        pct_near  = pct_near.iloc[::interval]

    # SPY series aligned
    spy_series = fetch_spy_close(period_str).reindex(pct_above.index, method="ffill")

    latest = float(pct_above.dropna().iloc[-1])

    # ---------- Plot: 2 rows of BAR charts ----------
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.10,
        subplot_titles=("Breadth vs SMA (Bars)", "SPY Close (Bars)")
    )

    # Row 1: Grouped bars for breadth
    fig.add_trace(
        go.Bar(x=pct_above.index, y=pct_above.values, name=f"≥ SMA{sma_window} (%)",
               marker=dict(opacity=0.9)),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=pct_near.index, y=pct_near.values, name=f"Within ±5% SMA{sma_window} (%)",
               marker=dict(opacity=0.65)),
        row=1, col=1
    )
    # 50% reference line
    fig.add_hline(y=50, line_width=1, line_dash="dash",
                  line_color="rgba(127,127,127,0.5)", row=1, col=1)

    # Row 2: SPY close bars
    fig.add_trace(
        go.Bar(x=spy_series.index, y=spy_series.values, name="SPY Close",
               marker=dict(opacity=0.85)),
        row=2, col=1
    )

    # Layout / aesthetics
    fig.update_layout(
        barmode="group",  # grouped bars in row 1
        height=760,
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
    fig.update_yaxes(title_text="% of S&P 500 symbols", rangemode="tozero",
                     gridcolor="rgba(255,255,255,0.08)", zeroline=False, row=1, col=1)
    fig.update_yaxes(title_text="SPY Close", gridcolor="rgba(255,255,255,0.08)",
                     zeroline=False, row=2, col=1)

    # Range slider on shared x (bottom subplot controls both)
    fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.06), row=2, col=1)

    status = f"Window={window_days}d • SMA={sma_window} • Interval={interval}d • Tickers≈{above.count(axis=1).iloc[-1]}"
    badge  = f"{latest:.1f}% ≥ SMA{sma_window}"

    return dcc.Graph(figure=fig, config={"displayModeBar": True}), status, badge