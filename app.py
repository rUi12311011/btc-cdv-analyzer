import streamlit as st
import requests
import pandas as pd
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="BTC CDV Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# TradingView風CSS
# =========================================================

st.markdown(
    """
    <style>
    /* Minimal monochrome / street-zine inspired UI */
    .stApp {
        background-color: #0b0b0c;
        color: #e6e2d9;
        font-family: Arial, Helvetica, sans-serif;
        font-size: 13px;
    }

    [data-testid="stAppViewContainer"] {
        background: #0b0b0c;
    }

    [data-testid="stSidebar"] {
        background-color: #111113;
        border-right: 1px solid #2b2b2f;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2.0rem;
    }

    .block-container {
        padding-top: 3.0rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .tv-header {
        background-color: #101012;
        border: 1px solid #2b2b2f;
        border-left: 4px solid #c1121f;
        border-radius: 2px;
        padding: 10px 14px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: none;
    }

    .tv-title {
        font-size: 18px;
        line-height: 1.2;
        font-weight: 700;
        color: #f4f1ea;
        letter-spacing: 0.2px;
        text-transform: uppercase;
    }

    .tv-subtitle {
        font-size: 11px;
        color: #9b9b9b;
        margin-top: 3px;
        letter-spacing: 0.1px;
    }

    .tv-badge {
        background-color: transparent;
        border: 1px solid #c1121f;
        border-radius: 2px;
        padding: 4px 8px;
        color: #f4f1ea;
        font-size: 10px;
        font-weight: 700;
        white-space: nowrap;
        letter-spacing: 0.5px;
    }

    .metric-card {
        background-color: #101012;
        border: 1px solid #2b2b2f;
        border-radius: 2px;
        padding: 9px 11px;
        margin-bottom: 8px;
    }

    .metric-label {
        font-size: 10px;
        color: #9b9b9b;
        margin-bottom: 3px;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    .metric-value {
        font-size: 14px;
        line-height: 1.35;
        font-weight: 600;
        color: #f4f1ea;
    }

    .metric-green { color: #9cc5a1; }
    .metric-red { color: #e45757; }

    label {
        color: #c8c3b8 !important;
        font-weight: 600 !important;
        font-size: 12px !important;
    }

    input, textarea, select {
        background-color: #18181b !important;
        color: #e6e2d9 !important;
        border: 1px solid #343438 !important;
        border-radius: 2px !important;
        font-size: 12px !important;
    }

    .stButton > button {
        background-color: #c1121f;
        color: #f4f1ea;
        border: 1px solid #c1121f;
        border-radius: 2px;
        padding: 0.45rem 0.9rem;
        font-size: 12px;
        font-weight: 700;
        width: 100%;
        letter-spacing: 0.3px;
    }

    .stButton > button:hover {
        background-color: #8f0d17;
        color: #ffffff;
        border-color: #8f0d17;
    }

    .stDownloadButton > button {
        background-color: #18181b;
        color: #e6e2d9;
        border: 1px solid #343438;
        border-radius: 2px;
        font-size: 12px;
        font-weight: 600;
    }

    .stDownloadButton > button:hover {
        background-color: #242428;
        color: #ffffff;
    }

    [data-testid="stDataFrame"] {
        background-color: #101012;
        border: 1px solid #2b2b2f;
        border-radius: 2px;
        overflow: hidden;
    }

    h1, h2, h3 {
        color: #f4f1ea !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px !important;
    }

    h1 { font-size: 1.35rem !important; }
    h2 { font-size: 1.05rem !important; }
    h3 { font-size: 0.9rem !important; }

    .stAlert {
        background-color: #141416;
        border: 1px solid #343438;
        border-left: 4px solid #c1121f;
        border-radius: 2px;
        color: #e6e2d9;
        font-size: 12px;
    }

    [data-testid="stMetric"] {
        background-color: #101012;
        border: 1px solid #2b2b2f;
        border-radius: 2px;
        padding: 9px;
    }

    hr { border-color: #2b2b2f; }

    .stCaptionContainer, .stMarkdown, .stText {
        font-size: 12px;
    }


    .side-icon-card {
        background-color: #0b0b0c;
        border: 1px solid #2b2b2f;
        border-left: 4px solid #c1121f;
        border-radius: 2px;
        padding: 9px 9px 7px 9px;
        margin: 0 0 14px 0;
    }

    .side-icon-title {
        font-size: 10px;
        line-height: 1;
        color: #f4f1ea;
        font-weight: 800;
        letter-spacing: 0.7px;
        text-transform: uppercase;
        margin-top: 3px;
    }

    .side-icon-sub {
        font-size: 9px;
        color: #8f8f8f;
        letter-spacing: 0.2px;
        margin-top: 3px;
    }

    .inflation-svg {
        width: 92px;
        height: auto;
        display: block;
    }

    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        gap: 0.35rem;
    }

    [data-testid="stSidebar"] .stCheckbox label {
        font-size: 11px !important;
        white-space: nowrap;
    }

    .tiny-status {
        display: inline-block;
        background-color: #101012;
        border-left: 3px solid #c1121f;
        color: #9b9b9b;
        font-size: 10.5px;
        line-height: 1.2;
        padding: 5px 8px;
        margin: 4px 0 10px 0;
        letter-spacing: 0.1px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="tv-header">
        <div>
            <div class="tv-title">Signal Flow Validator</div>
            <div class="tv-subtitle">
                TradingView signal check / Coinbase actual trade CVD / absorption / POC / squeeze
            </div>
        </div>
        <div class="tv-badge">LIVE DATA</div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 入力変換ヘルパー
# =========================================================

def safe_int_input(value, default, min_value=None, max_value=None):
    try:
        v = int(float(str(value).strip()))
    except Exception:
        v = default
    if min_value is not None:
        v = max(min_value, v)
    if max_value is not None:
        v = min(max_value, v)
    return v


def safe_float_input(value, default, min_value=None, max_value=None):
    try:
        v = float(str(value).strip())
    except Exception:
        v = default
    if min_value is not None:
        v = max(min_value, v)
    if max_value is not None:
        v = min(max_value, v)
    return v


# =========================================================
# サイドバー入力
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="side-icon-card">
            <svg class="inflation-svg" viewBox="0 0 180 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Inflation stencil icon">
                <rect x="0" y="0" width="180" height="120" fill="#0b0b0c"/>
                <path d="M36 76 C52 70, 65 68, 82 74 C93 78, 106 78, 120 72" fill="none" stroke="#f4f1ea" stroke-width="7" stroke-linecap="round" opacity="0.94"/>
                <path d="M42 79 L30 94 L53 88 Z" fill="#f4f1ea" opacity="0.94"/>
                <circle cx="124" cy="36" r="27" fill="#c1121f"/>
                <path d="M111 33 H138" stroke="#0b0b0c" stroke-width="7" stroke-linecap="square"/>
                <path d="M124 21 V50" stroke="#0b0b0c" stroke-width="7" stroke-linecap="square"/>
                <path d="M124 63 C121 73, 112 76, 104 80" fill="none" stroke="#f4f1ea" stroke-width="4" stroke-linecap="round" stroke-dasharray="5 5"/>
                <path d="M66 46 L93 38 L104 67 L76 76 Z" fill="none" stroke="#f4f1ea" stroke-width="5"/>
                <path d="M77 56 L90 52" stroke="#f4f1ea" stroke-width="4" stroke-linecap="round"/>
                <path d="M84 47 L89 64" stroke="#f4f1ea" stroke-width="4" stroke-linecap="round"/>
                <path d="M147 80 L147 50" stroke="#c1121f" stroke-width="7" stroke-linecap="square"/>
                <path d="M134 63 L147 50 L160 63" fill="none" stroke="#c1121f" stroke-width="7" stroke-linecap="square"/>
                <path d="M18 105 H162" stroke="#2b2b2f" stroke-width="3" stroke-dasharray="7 6"/>
            </svg>
            <div class="side-icon-title">INFLATION / FLOW</div>
            <div class="side-icon-sub">price rises, liquidity hides</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Settings")

    product_id = st.text_input("Product ID", value="BTC-USD")

    hours_back_raw = st.text_input("Hours Back", value="6")
    hours_back = safe_int_input(hours_back_raw, default=6, min_value=1, max_value=24)

    detail_5m_start_str = st.text_input(
        "Selected 5m Bar JST",
        value="2026-06-13 20:55:00"
    )

    price_round_digit = st.selectbox(
        "Price Bin Rounding",
        options=[0, 1, 2],
        index=1,
        format_func=lambda x: {
            0: "$1 step",
            1: "$0.1 step",
            2: "$0.01 step"
        }[x]
    )

    st.markdown("---")
    st.markdown("### Visible Icons")

    visible_icon_types = []
    icon_col1, icon_col2 = st.columns(2)

    with icon_col1:
        if st.checkbox("△ Buy Abs", value=True, key="vis_buy_abs"):
            visible_icon_types.append("Buy absorption")
        if st.checkbox("+ Buy Conf", value=True, key="vis_buy_conf"):
            visible_icon_types.append("Buy confirmation")
        if st.checkbox("★ Short", value=True, key="vis_short_sqz"):
            visible_icon_types.append("Short squeeze candidate")
        if st.checkbox("◇ High", value=True, key="vis_high_vol"):
            visible_icon_types.append("High volume")

    with icon_col2:
        if st.checkbox("▼ Sell Abs", value=True, key="vis_sell_abs"):
            visible_icon_types.append("Sell absorption")
        if st.checkbox("− Sell Conf", value=True, key="vis_sell_conf"):
            visible_icon_types.append("Sell confirmation")
        if st.checkbox("✳ Long", value=True, key="vis_long_sqz"):
            visible_icon_types.append("Long squeeze candidate")

    icon_type_options = [
        "Buy absorption",
        "Sell absorption",
        "Buy confirmation",
        "Sell confirmation",
        "Short squeeze candidate",
        "Long squeeze candidate",
        "High volume",
    ]

    st.markdown("---")
    st.markdown("### Confirmation / Sync Rules")

    confirm_vol_len_raw = st.text_input("Volume MA Length", value="20")
    confirm_vol_len = safe_int_input(confirm_vol_len_raw, default=20, min_value=5, max_value=200)

    confirm_vol_mult_raw = st.text_input("Volume Surge Multiplier", value="1.5")
    confirm_vol_mult = safe_float_input(confirm_vol_mult_raw, default=1.5, min_value=0.5, max_value=10.0)

    confirm_lookback_raw = st.text_input("CVD/Price Lookback Bars", value="3")
    confirm_lookback = safe_int_input(confirm_lookback_raw, default=3, min_value=1, max_value=50)

    confirm_require_full_window = st.checkbox(
        "Require Full MA Window",
        value=True
    )

    st.caption("TradingView signal validation: volume surge + price/CVD lookback alignment + current price/CVD candle alignment")

    st.markdown("---")

    run = st.button("Run Analysis")


# =========================================================
# Coinbase 約定履歴取得
# =========================================================

def fetch_coinbase_trades(
    product_id,
    range_start,
    range_end,
    tz="Asia/Tokyo",
    max_pages=1000,
    sleep_sec=0.15
):
    trade_url = f"https://api.exchange.coinbase.com/products/{product_id}/trades"

    all_rows = []
    after = None
    page = 0

    progress = st.progress(0)
    status = st.empty()

    while page < max_pages:
        params = {"limit": 1000}

        if after is not None:
            params["after"] = after

        res = requests.get(trade_url, params=params)

        if res.status_code != 200:
            st.error(f"約定履歴APIエラー: {res.status_code}")
            st.write(res.text)
            break

        trades = res.json()

        if not isinstance(trades, list) or len(trades) == 0:
            break

        rows = []

        for t in trades:
            time_utc = pd.to_datetime(t["time"], utc=True)
            time_jst = time_utc.tz_convert(tz)

            side = t["side"]

            # Coinbaseのsideはmaker側
            # Coinbaseのsideはmaker側
            # side=sell → ask側が約定 → taker direction は buy
            # side=buy  → bid側が約定 → taker direction は sell
            # bid/askではなく、ここでは実際にぶつけた側の方向として buy / sell で表示する
            taker_side = "buy" if side == "sell" else "sell"

            rows.append({
                "trade_id": int(t["trade_id"]),
                "time_jst": time_jst,
                "price": float(t["price"]),
                "size_BTC": float(t["size"]),
                "coinbase_side": side,
                "taker_side_estimate": taker_side
            })

        all_rows.extend(rows)

        df_temp = pd.DataFrame(all_rows).drop_duplicates(subset=["trade_id"])

        oldest = df_temp["time_jst"].min()
        newest = df_temp["time_jst"].max()

        status.write(
            f"取得中 page {page + 1} / 最新 {newest} / 最古 {oldest} / 件数 {len(df_temp)}"
        )

        progress.progress(min((page + 1) / 100, 1.0))

        if oldest <= range_start:
            break

        after = res.headers.get("CB-AFTER")

        if after is None:
            break

        page += 1
        time.sleep(sleep_sec)

    if len(all_rows) == 0:
        return pd.DataFrame()

    df_all = pd.DataFrame(all_rows).drop_duplicates(subset=["trade_id"])
    df_all = df_all.sort_values("time_jst")

    df_range = df_all[
        (df_all["time_jst"] >= range_start) &
        (df_all["time_jst"] < range_end)
    ].copy()

    return df_range.sort_values("time_jst")


# =========================================================
# Coinbase ローソク足取得
# =========================================================

def fetch_coinbase_candles(product_id, range_start, range_end, granularity=300):
    url = f"https://api.exchange.coinbase.com/products/{product_id}/candles"

    params = {
        "start": range_start.tz_convert("UTC").isoformat(),
        "end": range_end.tz_convert("UTC").isoformat(),
        "granularity": granularity
    }

    res = requests.get(url, params=params)

    if res.status_code != 200:
        st.error(f"ローソク足APIエラー: {res.status_code}")
        st.write(res.text)
        return pd.DataFrame()

    data = res.json()

    if not isinstance(data, list) or len(data) == 0:
        return pd.DataFrame()

    # Coinbase candles:
    # [time, low, high, open, close, volume]
    df = pd.DataFrame(
        data,
        columns=["time", "low", "high", "open", "close", "volume"]
    )

    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert("Asia/Tokyo")
    df = df.sort_values("time")

    return df


# =========================================================
# ローソク足チャート表示
# =========================================================

def show_candlestick_chart(df_candles, product_id, important_points=None, selected_point=None, sr_levels=None):
    if len(df_candles) == 0:
        st.warning("ローソク足データがありません。")
        return

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25]
    )

    fig.add_trace(
        go.Candlestick(
            x=df_candles["time"],
            open=df_candles["open"],
            high=df_candles["high"],
            low=df_candles["low"],
            close=df_candles["close"],
            # Light chart mode: buy candle = white, sell candle = black
            increasing_line_color="#111111",
            decreasing_line_color="#111111",
            increasing_fillcolor="#ffffff",
            decreasing_fillcolor="#111111",
            increasing_line_width=0.65,
            decreasing_line_width=0.65,
            name=product_id
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=df_candles["time"],
            y=df_candles["volume"],
            marker_color="#666666",
            name="Volume"
        ),
        row=2,
        col=1
    )

    # 重要ポイントをチャートにマーカー表示
    if important_points is not None and len(important_points) > 0:
        # Simple stencil-like icons. Shape differences carry the meaning more than color.
        marker_colors = {
            "Buy absorption": "#111111",
            "Sell absorption": "#111111",
            "Buy confirmation": "#111111",
            "Sell confirmation": "#111111",
            "Short squeeze candidate": "#c1121f",
            "Long squeeze candidate": "#c1121f",
            "High volume": "#4f4f4f"
        }

        marker_symbols = {
            "Buy absorption": "triangle-up-open",
            "Sell absorption": "triangle-down",
            "Buy confirmation": "cross-open",
            "Sell confirmation": "line-ew-open",
            "Short squeeze candidate": "star",
            "Long squeeze candidate": "asterisk",
            "High volume": "diamond-open"
        }

        marker_line_colors = {
            "Buy absorption": "#111111",
            "Sell absorption": "#111111",
            "Buy confirmation": "#111111",
            "Sell confirmation": "#111111",
            "Short squeeze candidate": "#c1121f",
            "Long squeeze candidate": "#c1121f",
            "High volume": "#4f4f4f"
        }

        marker_sizes = {
            "Buy absorption": 13,
            "Sell absorption": 13,
            "Buy confirmation": 16,
            "Sell confirmation": 20,
            "Short squeeze candidate": 15,
            "Long squeeze candidate": 15,
            "High volume": 12
        }

        marker_line_widths = {
            "Buy absorption": 1.3,
            "Sell absorption": 1.3,
            "Buy confirmation": 1.3,
            "Sell confirmation": 4.0,
            "Short squeeze candidate": 1.5,
            "Long squeeze candidate": 1.5,
            "High volume": 1.2
        }

        for point_type, group in important_points.groupby("type"):
            fig.add_trace(
                go.Scatter(
                    x=group["time_5m"],
                    y=group["spot_price"],
                    mode="markers",
                    marker=dict(
                        size=marker_sizes.get(point_type, 13),
                        color=marker_colors.get(point_type, "#ffffff"),
                        symbol=marker_symbols.get(point_type, "circle"),
                        line=dict(width=marker_line_widths.get(point_type, 1.3), color=marker_line_colors.get(point_type, "#111111"))
                    ),
                    name=point_type,
                    text=group["reason"],
                    hoverinfo="skip",
                    hovertemplate=None
                ),
                row=1,
                col=1
            )

            # Small deterministic spray dots around each icon for a stencil/spray feel
            try:
                price_span = max(float(df_candles["high"].max() - df_candles["low"].min()), 1.0)
                y_unit = price_span * 0.003
                spray_offsets = [
                    (-18, -0.8), (-9, 0.9), (12, -1.1), (21, 0.5)
                ]
                spray_x = []
                spray_y = []
                for _, g in group.iterrows():
                    for sec, y_mul in spray_offsets:
                        spray_x.append(g["time_5m"] + pd.Timedelta(seconds=sec))
                        spray_y.append(float(g["spot_price"]) + y_unit * y_mul)

                fig.add_trace(
                    go.Scatter(
                        x=spray_x,
                        y=spray_y,
                        mode="markers",
                        marker=dict(
                            size=3,
                            color=marker_colors.get(point_type, "#111111"),
                            opacity=0.35,
                            line=dict(width=0)
                        ),
                        showlegend=False,
                        hoverinfo="skip",
                        name=f"{point_type} spray"
                    ),
                    row=1,
                    col=1
                )
            except Exception:
                pass

    # POC / Support / Resistance Candidatesの水平線
    if sr_levels is not None and len(sr_levels) > 0:
        for _, level in sr_levels.iterrows():
            kind = level["kind"]
            price = float(level["price"])
            volume = float(level["volume_BTC"])

            if kind == "POC":
                color = "#c1121f"
                dash = "solid"
            elif kind == "Support":
                color = "#5f5f5f"
                dash = "dot"
            else:
                color = "#111111"
                dash = "dot"

            # SR/POCラベルは価格が近いと重なるため、チャート上には線だけ表示。
            # 詳細は下のPOC / Support / Resistanceテーブルで確認。
            fig.add_hline(
                y=price,
                line_color=color,
                line_dash=dash,
                line_width=2,
                row=1,
                col=1
            )

    # 選択したポイントをスポット表示
    if selected_point is not None:
        selected_time = selected_point["time_5m"]
        selected_start = selected_time - pd.Timedelta(minutes=2, seconds=30)
        selected_end = selected_time + pd.Timedelta(minutes=2, seconds=30)
        selected_price = selected_point["spot_price"]
        selected_label = selected_point["label"]

        # Spotは青い帯を使わず、ローソク中央の細い縦線だけにする。
        fig.add_vline(
            x=selected_time,
            line_color="#c1121f",
            line_width=1,
            line_dash="dash",
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=[selected_time],
                y=[selected_price],
                mode="markers",
                marker=dict(
                    size=16,
                    color="#ffffff",
                    symbol="circle-open",
                    line=dict(width=2, color="#c1121f")
                ),
                name="Selected Spot",
                hoverinfo="skip",
                hovertemplate=None
            ),
            row=1,
            col=1
        )


    fig.update_layout(
        height=780,
        xaxis_rangeslider_visible=False,
        title="",
        template="plotly_white",
        paper_bgcolor="#9b9b9b",
        plot_bgcolor="#9b9b9b",
        font=dict(color="#111111"),
        margin=dict(l=20, r=70, t=12, b=120),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(170, 170, 170, 0.95)",
            bordercolor="#111111",
            borderwidth=1
        )
    )

    fig.update_xaxes(
        gridcolor="#7e7e7e",
        zerolinecolor="#6d6d6d",
        rangeslider_visible=False
    )

    fig.update_yaxes(
        gridcolor="#7e7e7e",
        zerolinecolor="#9e9e9e"
    )

    return st.plotly_chart(
        fig,
        use_container_width=True,
        key="main_chart"
    )


# =========================================================
# 5分足CDV集計
# =========================================================

def make_5m_summary(df_range, confirm_vol_len=20, confirm_vol_mult=1.5, confirm_lookback=3, confirm_require_full_window=True):
    df_range = df_range.copy()

    df_range["time_5m"] = df_range["time_jst"].dt.floor("5min")

    grouped = df_range.groupby("time_5m")

    summary_5m = grouped.agg(
        open=("price", "first"),
        high=("price", "max"),
        low=("price", "min"),
        close=("price", "last"),
        volume_BTC=("size_BTC", "sum"),
        trade_count=("trade_id", "count")
    )

    buy_5m = (
        df_range[df_range["taker_side_estimate"] == "buy"]
        .groupby("time_5m")["size_BTC"]
        .sum()
    )

    sell_5m = (
        df_range[df_range["taker_side_estimate"] == "sell"]
        .groupby("time_5m")["size_BTC"]
        .sum()
    )

    summary_5m["buy_taker_BTC"] = buy_5m
    summary_5m["sell_taker_BTC"] = sell_5m

    summary_5m["buy_taker_BTC"] = summary_5m["buy_taker_BTC"].fillna(0)
    summary_5m["sell_taker_BTC"] = summary_5m["sell_taker_BTC"].fillna(0)

    summary_5m["delta_BTC"] = (
        summary_5m["buy_taker_BTC"] -
        summary_5m["sell_taker_BTC"]
    )

    summary_5m["buy_ratio_%"] = (
        summary_5m["buy_taker_BTC"] /
        summary_5m["volume_BTC"] *
        100
    )

    summary_5m["sell_ratio_%"] = (
        summary_5m["sell_taker_BTC"] /
        summary_5m["volume_BTC"] *
        100
    )

    summary_5m["candle_move"] = summary_5m["close"] - summary_5m["open"]
    summary_5m["range"] = summary_5m["high"] - summary_5m["low"]

    # 吸収判定用
    # 吸収 = 大きいデルタが出ているのに、実体が小さい / 価格が進んでいない状態
    summary_5m["body_abs"] = summary_5m["candle_move"].abs()
    summary_5m["delta_abs"] = summary_5m["delta_BTC"].abs()
    summary_5m["delta_strength"] = summary_5m["delta_abs"] / summary_5m["volume_BTC"]
    summary_5m["body_to_range"] = summary_5m["body_abs"] / summary_5m["range"].replace(0, pd.NA)

    # 価格が動いていない判定：実体が小さい
    # 15ドル以下、またはその足の値幅の35%以下なら「進みが弱い」と見る
    summary_5m["absorption_body_limit"] = (summary_5m["range"] * 0.35).clip(lower=15)
    summary_5m["price_not_moved"] = summary_5m["body_abs"] <= summary_5m["absorption_body_limit"]

    # 選択期間内で相対的に大きいデルタを抽出
    delta_threshold = summary_5m["delta_abs"].quantile(0.60)

    # sell deltaが大きいのに価格が下に進まない = Buy absorption candidates
    summary_5m["buy_absorption_candidate"] = (
        (summary_5m["delta_BTC"] <= -delta_threshold) &
        (summary_5m["delta_strength"] >= 0.25) &
        (summary_5m["price_not_moved"])
    )

    # 確認足判定
    # PineのbullSync / bearSyncに近い条件
    # volSurge + priceLookback方向 + CVDLookback方向 + 価格足方向 + CVD足方向
    confirm_min_periods = int(confirm_vol_len) if confirm_require_full_window else max(3, int(confirm_vol_len) // 4)
    confirm_lookback = int(confirm_lookback)

    summary_5m["confirm_vol_avg"] = (
        summary_5m["volume_BTC"]
        .rolling(int(confirm_vol_len), min_periods=confirm_min_periods)
        .mean()
        .shift(1)
    )

    summary_5m["confirm_vol_mult_actual"] = (
        summary_5m["volume_BTC"] / summary_5m["confirm_vol_avg"]
    )

    summary_5m["confirm_volume_ok"] = (
        summary_5m["confirm_vol_avg"].notna() &
        (summary_5m["volume_BTC"] >= summary_5m["confirm_vol_avg"] * float(confirm_vol_mult))
    )

    # Coinbase実約定ベースCVD
    # buy takerっぽい - sell takerっぽい の5分足デルタを累積
    summary_5m["cumulative_delta_BTC"] = summary_5m["delta_BTC"].cumsum()

    summary_5m["price_up_lookback"] = summary_5m["close"] > summary_5m["close"].shift(confirm_lookback)
    summary_5m["price_down_lookback"] = summary_5m["close"] < summary_5m["close"].shift(confirm_lookback)

    summary_5m["cvd_up_lookback"] = summary_5m["cumulative_delta_BTC"] > summary_5m["cumulative_delta_BTC"].shift(confirm_lookback)
    summary_5m["cvd_down_lookback"] = summary_5m["cumulative_delta_BTC"] < summary_5m["cumulative_delta_BTC"].shift(confirm_lookback)

    summary_5m["price_bull_candle"] = summary_5m["candle_move"] > 0
    summary_5m["price_bear_candle"] = summary_5m["candle_move"] < 0

    # CVD candleは5分足内の実約定デルタ方向
    summary_5m["cvd_bull_candle"] = summary_5m["delta_BTC"] > 0
    summary_5m["cvd_bear_candle"] = summary_5m["delta_BTC"] < 0

    summary_5m["delta_price_same_up"] = (
        summary_5m["cvd_bull_candle"] &
        summary_5m["price_bull_candle"]
    )

    summary_5m["delta_price_same_down"] = (
        summary_5m["cvd_bear_candle"] &
        summary_5m["price_bear_candle"]
    )

    summary_5m["bullish_confirmation"] = (
        summary_5m["confirm_volume_ok"] &
        summary_5m["price_up_lookback"] &
        summary_5m["cvd_up_lookback"] &
        summary_5m["price_bull_candle"] &
        summary_5m["cvd_bull_candle"]
    )

    # buy deltaが大きいのに価格が上に進まない = Sell absorption candidates
    summary_5m["sell_absorption_candidate"] = (
        (summary_5m["delta_BTC"] >= delta_threshold) &
        (summary_5m["delta_strength"] >= 0.25) &
        (summary_5m["price_not_moved"])
    )

    summary_5m["bearish_confirmation"] = (
        summary_5m["confirm_volume_ok"] &
        summary_5m["price_down_lookback"] &
        summary_5m["cvd_down_lookback"] &
        summary_5m["price_bear_candle"] &
        summary_5m["cvd_bear_candle"]
    )

    summary_5m["lower_wick"] = (
        summary_5m[["open", "close"]].min(axis=1) -
        summary_5m["low"]
    )

    summary_5m["upper_wick"] = (
        summary_5m["high"] -
        summary_5m[["open", "close"]].max(axis=1)
    )

    vol_median = summary_5m["volume_BTC"].median()

    summary_5m["defense_score"] = 0

    summary_5m.loc[summary_5m["buy_absorption_candidate"], "defense_score"] += 2
    summary_5m.loc[summary_5m["volume_BTC"] >= vol_median, "defense_score"] += 1
    summary_5m.loc[summary_5m["lower_wick"] > 0, "defense_score"] += 1
    summary_5m.loc[summary_5m["candle_move"] > 0, "defense_score"] += 1

    return summary_5m




# =========================================================
# POC / Support / Resistance Candidates
# =========================================================

def calculate_volume_profile_levels(df_range, current_price, price_round_digit, top_n=3):
    df = df_range.copy()
    df["price_bin"] = df["price"].round(price_round_digit)

    volume_by_price_all = (
        df
        .groupby("price_bin")["size_BTC"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    side_price_volume_all = (
        df
        .groupby(["price_bin", "taker_side_estimate"])["size_BTC"]
        .sum()
        .unstack(fill_value=0)
    )

    side_price_volume_all["合計"] = side_price_volume_all.sum(axis=1)
    side_price_volume_all = side_price_volume_all.sort_values("合計", ascending=False)

    levels = []

    if len(volume_by_price_all) == 0:
        return volume_by_price_all, side_price_volume_all, pd.DataFrame()

    poc = volume_by_price_all.iloc[0]
    levels.append({
        "kind": "POC",
        "price": float(poc["price_bin"]),
        "volume_BTC": float(poc["size_BTC"]),
        "distance_from_current": float(poc["price_bin"] - current_price),
        "memo": "選択期間内で最も出来高が集中した価格帯"
    })

    supports = (
        volume_by_price_all[volume_by_price_all["price_bin"] < current_price]
        .sort_values("size_BTC", ascending=False)
        .head(top_n)
    )

    resistances = (
        volume_by_price_all[volume_by_price_all["price_bin"] > current_price]
        .sort_values("size_BTC", ascending=False)
        .head(top_n)
    )

    for _, r in supports.iterrows():
        levels.append({
            "kind": "Support",
            "price": float(r["price_bin"]),
            "volume_BTC": float(r["size_BTC"]),
            "distance_from_current": float(r["price_bin"] - current_price),
            "memo": "High-volume area below current price. Support candidate."
        })

    for _, r in resistances.iterrows():
        levels.append({
            "kind": "Resistance",
            "price": float(r["price_bin"]),
            "volume_BTC": float(r["size_BTC"]),
            "distance_from_current": float(r["price_bin"] - current_price),
            "memo": "High-volume area above current price. Resistance candidate."
        })

    sr_levels = pd.DataFrame(levels)
    sr_levels = sr_levels.drop_duplicates(subset=["kind", "price"])

    return volume_by_price_all, side_price_volume_all, sr_levels


# =========================================================
# 重要ポイント自動抽出
# =========================================================

def detect_important_points(summary_5m):
    rows = []

    if summary_5m is None or len(summary_5m) == 0:
        return pd.DataFrame()

    df = summary_5m.copy().reset_index()

    vol_threshold = df["volume_BTC"].quantile(0.80)

    for i, row in df.iterrows():
        t = row["time_5m"]
        base = {
            "time_5m": t,
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "spot_price": row["close"],
            "volume_BTC": row["volume_BTC"],
            "delta_BTC": row["delta_BTC"],
            "cumulative_delta_BTC": row.get("cumulative_delta_BTC", pd.NA),
            "buy_ratio_%": row["buy_ratio_%"],
            "sell_ratio_%": row["sell_ratio_%"],
            "candle_move": row["candle_move"],
            "delta_strength": row.get("delta_strength", abs(row["delta_BTC"]) / row["volume_BTC"] if row["volume_BTC"] else 0),
            "price_not_moved": row.get("price_not_moved", False),
            "confirm_vol_avg": row.get("confirm_vol_avg", pd.NA),
            "confirm_vol_mult_actual": row.get("confirm_vol_mult_actual", pd.NA),
            "confirm_volume_ok": row.get("confirm_volume_ok", False),
        }

        if row["buy_absorption_candidate"]:
            score = 80 + min(15, row.get("delta_strength", 0) * 30)
            rows.append({
                **base,
                "type": "Buy absorption",
                "score": round(score, 1),
                "reason": f"Sell delta {row['delta_BTC']:.2f} BTC vs body {row['candle_move']:.2f} USD. Sell flow appeared, but price did not move down enough. Buy absorption candidate."
            })

        if row["bullish_confirmation"]:
            mult = row.get("confirm_vol_mult_actual", 0)
            score = 78 + min(18, max(0, float(mult) - 2.0) * 6)
            rows.append({
                **base,
                "spot_price": row["low"] - max(row["range"] * 0.20, 8),
                "type": "Buy confirmation",
                "score": round(score, 1),
                "reason": f"Volume {row['volume_BTC']:.2f} BTC is {mult:.2f}x the recent average. Price/CVD lookback is up, with delta +{row['delta_BTC']:.2f} BTC and candle move +{row['candle_move']:.2f} USD aligned upward. Buy confirmation."
            })

        if row["sell_absorption_candidate"]:
            score = 80 + min(15, row.get("delta_strength", 0) * 30)
            rows.append({
                **base,
                "type": "Sell absorption",
                "score": round(score, 1),
                "reason": f"Buy delta +{row['delta_BTC']:.2f} BTC vs body {row['candle_move']:.2f} USD. Buy flow appeared, but price did not move up enough. Sell absorption candidate."
            })

        if row["bearish_confirmation"]:
            mult = row.get("confirm_vol_mult_actual", 0)
            score = 78 + min(18, max(0, float(mult) - 2.0) * 6)
            rows.append({
                **base,
                "spot_price": row["high"] + max(row["range"] * 0.20, 8),
                "type": "Sell confirmation",
                "score": round(score, 1),
                "reason": f"Volume {row['volume_BTC']:.2f} BTC is {mult:.2f}x the recent average. Price/CVD lookback is down, with delta {row['delta_BTC']:.2f} BTC and candle move {row['candle_move']:.2f} USD aligned downward. Sell confirmation."
            })

        if row["volume_BTC"] >= vol_threshold:
            rows.append({
                **base,
                "type": "High volume",
                "score": 60,
                "reason": f"Top 20% volume within the selected period. High-volume point."
            })

    # スクイーズ候補：吸収のあと数本以内に確認足が出たところを強調
    for i, row in df.iterrows():
        future = df.iloc[i+1:i+4]

        if row["buy_absorption_candidate"] and len(future) > 0 and future["bullish_confirmation"].any():
            confirm = future[future["bullish_confirmation"]].iloc[0]
            rows.append({
                "time_5m": confirm["time_5m"],
                "open": confirm["open"],
                "high": confirm["high"],
                "low": confirm["low"],
                "close": confirm["close"],
                "spot_price": confirm["close"],
                "volume_BTC": confirm["volume_BTC"],
                "delta_BTC": confirm["delta_BTC"],
                "buy_ratio_%": confirm["buy_ratio_%"],
                "sell_ratio_%": confirm["sell_ratio_%"],
                "candle_move": confirm["candle_move"],
                "type": "Short squeeze candidate",
                "score": 95,
                "reason": f"After Buy absorption at {row['time_5m']}, Buy confirmation appeared at {confirm['time_5m']}. Short squeeze candidate."
            })

        if row["sell_absorption_candidate"] and len(future) > 0 and future["bearish_confirmation"].any():
            confirm = future[future["bearish_confirmation"]].iloc[0]
            rows.append({
                "time_5m": confirm["time_5m"],
                "open": confirm["open"],
                "high": confirm["high"],
                "low": confirm["low"],
                "close": confirm["close"],
                "spot_price": confirm["close"],
                "volume_BTC": confirm["volume_BTC"],
                "delta_BTC": confirm["delta_BTC"],
                "buy_ratio_%": confirm["buy_ratio_%"],
                "sell_ratio_%": confirm["sell_ratio_%"],
                "candle_move": confirm["candle_move"],
                "type": "Long squeeze candidate",
                "score": 95,
                "reason": f"After Sell absorption at {row['time_5m']}, Sell confirmation appeared at {confirm['time_5m']}. Long squeeze candidate."
            })

    # 追加ルール：Sell confirmation bars/ショート誘い込み後の強い上抜け
    # これは「Buy absorption → Buy confirmation」では拾えないショートスクイーズ型を拾うため。
    for i, row in df.iterrows():
        if i == 0:
            continue

        prev = df.iloc[i - 1]
        lookback = df.iloc[max(0, i - 6):i]

        if len(lookback) == 0:
            continue

        previous_high = lookback["high"].max()
        previous_low = lookback["low"].min()
        recent_sell_pressure = (lookback["sell_ratio_%"] >= 60).any()
        recent_buy_pressure = (lookback["buy_ratio_%"] >= 60).any()

        # Short squeeze candidate：直前に売り圧があり、その後にBuy confirmation＋直近高値上抜け
        if (
            row.get("bullish_confirmation", False) and
            row["high"] > previous_high and
            recent_sell_pressure
        ):
            rows.append({
                "time_5m": row["time_5m"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "spot_price": row["close"],
                "volume_BTC": row["volume_BTC"],
                "delta_BTC": row["delta_BTC"],
                "buy_ratio_%": row["buy_ratio_%"],
                "sell_ratio_%": row["sell_ratio_%"],
                "candle_move": row["candle_move"],
                "type": "Short squeeze candidate",
                "score": 96,
                "reason": f"After recent sell pressure, buy taker ratio reached {row['buy_ratio_%']:.1f}% and price broke above recent high {previous_high:.2f}. Short squeeze candidate."
            })

        # ベアトラップ型：直前足が売り優勢、その次足で強い買い反転
        if (
            prev["sell_ratio_%"] >= 70 and
            prev["candle_move"] <= 0 and
            row.get("bullish_confirmation", False) and
            row["close"] > prev["open"]
        ):
            rows.append({
                "time_5m": row["time_5m"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "spot_price": row["close"],
                "volume_BTC": row["volume_BTC"],
                "delta_BTC": row["delta_BTC"],
                "buy_ratio_%": row["buy_ratio_%"],
                "sell_ratio_%": row["sell_ratio_%"],
                "candle_move": row["candle_move"],
                "type": "Short squeeze candidate",
                "score": 98,
                "reason": f"Previous bar had sell taker ratio {prev['sell_ratio_%']:.1f}%, likely trapping shorts. Next bar reversed upward with buy taker ratio {row['buy_ratio_%']:.1f}%. Bear-trap short squeeze candidate."
            })

        # Long squeeze candidate：直近に買い圧があり、その後にSell confirmation＋直近安値割れ
        if (
            row.get("bearish_confirmation", False) and
            row["low"] < previous_low and
            recent_buy_pressure
        ):
            rows.append({
                "time_5m": row["time_5m"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "spot_price": row["close"],
                "volume_BTC": row["volume_BTC"],
                "delta_BTC": row["delta_BTC"],
                "buy_ratio_%": row["buy_ratio_%"],
                "sell_ratio_%": row["sell_ratio_%"],
                "candle_move": row["candle_move"],
                "type": "Long squeeze candidate",
                "score": 96,
                "reason": f"After recent buy pressure, sell taker ratio reached {row['sell_ratio_%']:.1f}% and price broke below recent low {previous_low:.2f}. Long squeeze candidate."
            })

    if not rows:
        return pd.DataFrame()

    points = pd.DataFrame(rows)
    points = points.drop_duplicates(subset=["time_5m", "type"])
    points = points.sort_values(["score", "volume_BTC"], ascending=False).reset_index(drop=True)

    points["No"] = range(1, len(points) + 1)
    points["point_id"] = points.apply(
        lambda r: f"{r['time_5m'].isoformat()}__{r['type']}__{r['No']}",
        axis=1
    )
    points["label"] = points.apply(
        lambda r: f"{int(r['No'])}. {r['time_5m'].strftime('%m/%d %H:%M')} | {r['type']} | score {r['score']} | close {r['close']:.2f}",
        axis=1
    )

    # Icon rail placement:
    # Do not stack icons directly on price. Put them slightly above bullish/neutral candles,
    # and below bearish candles. Multiple icons on the same bar are lined up with slots.
    points["icon_side"] = points["candle_move"].apply(lambda x: "below" if x < 0 else "above")

    points = points.sort_values(["time_5m", "icon_side", "score"], ascending=[True, True, False]).reset_index(drop=True)
    points["icon_slot"] = points.groupby(["time_5m", "icon_side"]).cumcount()

    def _icon_y(r):
        bar_range = max(float(r["high"] - r["low"]), 1.0)
        step = max(bar_range * 0.16, 10.0)
        if r["icon_side"] == "below":
            return float(r["low"] - step * (r["icon_slot"] + 1))
        return float(r["high"] + step * (r["icon_slot"] + 1))

    points["spot_price"] = points.apply(_icon_y, axis=1)

    # Re-sort by importance for the table after calculating rail positions.
    points = points.sort_values(["score", "volume_BTC"], ascending=False).reset_index(drop=True)
    points["No"] = range(1, len(points) + 1)
    points["point_id"] = points.apply(
        lambda r: f"{r['time_5m'].isoformat()}__{r['type']}__{r['No']}",
        axis=1
    )
    points["label"] = points.apply(
        lambda r: f"{int(r['No'])}. {r['time_5m'].strftime('%m/%d %H:%M')} | {r['type']} | score {r['score']} | close {r['close']:.2f}",
        axis=1
    )

    return points


# =========================================================
# 特定5分足の詳細解析
# =========================================================

def analyze_detail_5m(df_range, detail_start, price_round_digit):
    detail_end = detail_start + pd.Timedelta(minutes=5)

    df_detail = df_range[
        (df_range["time_jst"] >= detail_start) &
        (df_range["time_jst"] < detail_end)
    ].copy()

    if len(df_detail) == 0:
        return None

    df_detail = df_detail.sort_values("time_jst")

    total = df_detail["size_BTC"].sum()

    buy_qty = df_detail[
        df_detail["taker_side_estimate"] == "buy"
    ]["size_BTC"].sum()

    sell_qty = df_detail[
        df_detail["taker_side_estimate"] == "sell"
    ]["size_BTC"].sum()

    detail_summary = pd.DataFrame([{
        "start": detail_start,
        "end": detail_end,
        "open": df_detail.iloc[0]["price"],
        "high": df_detail["price"].max(),
        "low": df_detail["price"].min(),
        "close": df_detail.iloc[-1]["price"],
        "candle_move": df_detail.iloc[-1]["price"] - df_detail.iloc[0]["price"],
        "volume_BTC": total,
        "trade_count": len(df_detail),
        "buy_taker_BTC": buy_qty,
        "sell_taker_BTC": sell_qty,
        "delta_BTC": buy_qty - sell_qty,
        "buy_ratio_%": buy_qty / total * 100 if total > 0 else 0,
        "sell_ratio_%": sell_qty / total * 100 if total > 0 else 0
    }])

    df_detail["price_bin"] = df_detail["price"].round(price_round_digit)

    volume_by_price = (
        df_detail
        .groupby("price_bin")["size_BTC"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    side_price_volume = (
        df_detail
        .groupby(["price_bin", "taker_side_estimate"])["size_BTC"]
        .sum()
        .unstack(fill_value=0)
    )

    side_price_volume["合計"] = side_price_volume.sum(axis=1)
    side_price_volume = side_price_volume.sort_values("合計", ascending=False)

    df_detail["second"] = df_detail["time_jst"].dt.floor("s")

    volume_by_second = (
        df_detail
        .groupby(["second", "taker_side_estimate"])["size_BTC"]
        .sum()
        .unstack(fill_value=0)
    )

    volume_by_second["合計"] = volume_by_second.sum(axis=1)
    volume_by_second = volume_by_second.sort_values("合計", ascending=False)

    same_time = (
        df_detail
        .groupby("time_jst")
        .agg(
            count=("trade_id", "count"),
            total_BTC=("size_BTC", "sum"),
            min_price=("price", "min"),
            max_price=("price", "max")
        )
        .sort_values("count", ascending=False)
        .reset_index()
    )

    same_size = (
        df_detail
        .groupby(["size_BTC", "taker_side_estimate"])
        .agg(
            count=("trade_id", "count"),
            total_BTC=("size_BTC", "sum"),
            min_time=("time_jst", "min"),
            max_time=("time_jst", "max")
        )
        .sort_values("count", ascending=False)
        .reset_index()
    )

    df_seq = df_detail.sort_values("time_jst").copy()

    df_seq["group"] = (
        df_seq["taker_side_estimate"] !=
        df_seq["taker_side_estimate"].shift()
    ).cumsum()

    runs = (
        df_seq
        .groupby(["group", "taker_side_estimate"])
        .agg(
            count=("trade_id", "count"),
            total_BTC=("size_BTC", "sum"),
            start_time=("time_jst", "min"),
            end_time=("time_jst", "max"),
            min_price=("price", "min"),
            max_price=("price", "max")
        )
        .reset_index()
    )

    runs["duration_sec"] = (
        runs["end_time"] -
        runs["start_time"]
    ).dt.total_seconds()

    runs["price_move"] = runs["max_price"] - runs["min_price"]

    runs = runs.sort_values("total_BTC", ascending=False)

    return {
        "df_detail": df_detail,
        "detail_summary": detail_summary,
        "volume_by_price": volume_by_price,
        "side_price_volume": side_price_volume,
        "volume_by_second": volume_by_second,
        "same_time": same_time,
        "same_size": same_size,
        "runs": runs
    }


# =========================================================
# メトリックカード
# =========================================================

def metric_card(label, value, color_class=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value {color_class}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 画面描画
# =========================================================

def render_analysis(data):
    product_id = data["product_id"]
    range_start = data["range_start"]
    range_end = data["range_end"]
    df_candles = data["df_candles"]
    df_range = data["df_range"]
    summary_5m = data["summary_5m"]
    important_points = data["important_points"]
    volume_by_price_all = data["volume_by_price_all"]
    side_price_volume_all = data["side_price_volume_all"]
    sr_levels = data["sr_levels"]

    # Old session data may still contain Japanese point labels. Normalize to English.
    type_rename_map = {
        "買い吸収": "Buy absorption",
        "売り吸収": "Sell absorption",
        "買い確認": "Buy confirmation",
        "売り確認": "Sell confirmation",
        "ショートスクイーズ候補": "Short squeeze candidate",
        "ロングスクイーズ候補": "Long squeeze candidate",
        "高出来高": "High volume",
    }

    if important_points is not None and len(important_points) > 0 and "type" in important_points.columns:
        important_points = important_points.copy()
        important_points["type"] = important_points["type"].replace(type_rename_map)
        if "No" not in important_points.columns:
            important_points["No"] = range(1, len(important_points) + 1)
        important_points["point_id"] = important_points.apply(
            lambda r: f"{pd.Timestamp(r['time_5m']).isoformat()}__{r['type']}__{r['No']}",
            axis=1
        )
        important_points["label"] = important_points.apply(
            lambda r: f"{int(r['No'])}. {pd.Timestamp(r['time_5m']).strftime('%m/%d %H:%M')} | {r['type']} | score {r['score']} | close {r['close']:.2f}",
            axis=1
        )
        data["important_points"] = important_points

    # 旧バージョンで保存されたsession_state対策
    # app.py更新直後に古いimportant_pointsが残っているとpoint_idが無くてKeyErrorになるため補完する
    if important_points is not None and len(important_points) > 0 and "point_id" not in important_points.columns:
        important_points = important_points.copy()
        if "No" not in important_points.columns:
            important_points["No"] = range(1, len(important_points) + 1)
        important_points["point_id"] = important_points.apply(
            lambda r: f"{pd.Timestamp(r['time_5m']).isoformat()}__{r['type']}__{r['No']}",
            axis=1
        )
        if "label" not in important_points.columns:
            important_points["label"] = important_points.apply(
                lambda r: f"{int(r['No'])}. {pd.Timestamp(r['time_5m']).strftime('%m/%d %H:%M')}｜{r['type']}｜score {r['score']}｜close {r['close']:.2f}",
                axis=1
            )
        data["important_points"] = important_points

    st.markdown(
        f'<div class="tiny-status">Data: {range_start.strftime("%Y-%m-%d %H:%M")} – {range_end.strftime("%Y-%m-%d %H:%M")}</div>',
        unsafe_allow_html=True
    )

    selected_point = None

    if len(important_points) > 0:
        valid_ids = important_points["point_id"].tolist()

        if "selected_point_id" not in st.session_state or st.session_state["selected_point_id"] not in valid_ids:
            st.session_state["selected_point_id"] = valid_ids[0]

        st.subheader("Important Points")

        display_points = important_points.copy().reset_index(drop=True)
        display_points["Focus"] = display_points["point_id"] == st.session_state["selected_point_id"]
        display_points["time"] = display_points["time_5m"].dt.strftime("%m/%d %H:%M")

        editor_df = display_points[[
            "Focus", "No", "time", "type", "score", "reason",
            "open", "high", "low", "close",
            "volume_BTC", "delta_BTC",
            "buy_ratio_%", "sell_ratio_%"
        ]]

        edited_points = st.data_editor(
            editor_df,
            use_container_width=True,
            hide_index=True,
            disabled=[
                "No", "time", "type", "score", "reason",
                "open", "high", "low", "close",
                "volume_BTC", "delta_BTC",
                "buy_ratio_%", "sell_ratio_%"
            ],
            column_config={
                "Focus": st.column_config.CheckboxColumn(
                    "Focus",
                    help="Check one row to update Selected Point Details.",
                    default=False
                )
            },
            key=f"important_points_editor_{product_id}_{range_start.strftime('%Y%m%d%H%M%S')}_{range_end.strftime('%Y%m%d%H%M%S')}_{len(important_points)}"
        )

        checked_rows = edited_points.index[edited_points["Focus"] == True].tolist()
        if checked_rows:
            current_rows = display_points.index[display_points["point_id"] == st.session_state["selected_point_id"]].tolist()
            current_row = current_rows[0] if current_rows else None
            new_rows = [r for r in checked_rows if r != current_row]
            chosen_row = new_rows[-1] if new_rows else checked_rows[-1]
            new_point_id = display_points.iloc[chosen_row]["point_id"]
            if new_point_id != st.session_state["selected_point_id"]:
                st.session_state["selected_point_id"] = new_point_id
                st.rerun()

        selected_point = important_points[
            important_points["point_id"] == st.session_state["selected_point_id"]
        ].iloc[0]

    st.subheader("Coinbase 5m Chart")

    chart_points = important_points
    if len(important_points) > 0 and len(visible_icon_types) > 0:
        chart_points = important_points[important_points["type"].isin(visible_icon_types)].copy()
    elif len(visible_icon_types) == 0:
        chart_points = important_points.iloc[0:0].copy()

    if len(visible_icon_types) != len(icon_type_options):
        st.markdown(
            f'<div class="tiny-status">Icon filter: {", ".join(visible_icon_types) if visible_icon_types else "None"}</div>',
            unsafe_allow_html=True
        )

    show_candlestick_chart(
        df_candles,
        product_id,
        important_points=chart_points,
        selected_point=selected_point,
        sr_levels=sr_levels
    )

    if selected_point is not None:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Selected Point Details</div>
                <div class="metric-value">{selected_point['label']}</div>
                <div class="metric-label" style="margin-top:6px;">Reason</div>
                <div style="font-size:11px; line-height:1.45; color:#c8c3b8;">{selected_point['reason']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if len(sr_levels) > 0:
        st.subheader("POC / Support / Resistance Candidates")
        st.dataframe(sr_levels, use_container_width=True)

    latest = summary_5m.tail(1).iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Latest Close", f"{latest['close']:.2f}")

    with col2:
        color = "metric-green" if latest["delta_BTC"] >= 0 else "metric-red"
        metric_card("Latest Delta BTC", f"{latest['delta_BTC']:.4f}", color)

    with col3:
        metric_card("Buy Ratio", f"{latest['buy_ratio_%']:.2f}%", "metric-green")

    with col4:
        metric_card("Sell Ratio", f"{latest['sell_ratio_%']:.2f}%", "metric-red")

    st.subheader("5m CDV Summary - Latest 30 Bars")
    st.dataframe(summary_5m.tail(30), use_container_width=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Buy absorption candidates",
        "Buy confirmation bars",
        "Sell absorption candidates",
        "Sell confirmation bars",
        "Defense Line Candidates"
    ])

    with tab1:
        st.dataframe(
            summary_5m[summary_5m["buy_absorption_candidate"]],
            use_container_width=True
        )

    with tab2:
        st.dataframe(
            summary_5m[summary_5m["bullish_confirmation"]],
            use_container_width=True
        )

    with tab3:
        st.dataframe(
            summary_5m[summary_5m["sell_absorption_candidate"]],
            use_container_width=True
        )

    with tab4:
        st.dataframe(
            summary_5m[summary_5m["bearish_confirmation"]],
            use_container_width=True
        )

    with tab5:
        defense_candidates = (
            summary_5m[summary_5m["defense_score"] >= 3]
            .sort_values(
                ["defense_score", "volume_BTC"],
                ascending=False
            )
        )
        st.dataframe(defense_candidates, use_container_width=True)

    # -----------------------------------------------------
    # 全体Volume by Price
    # -----------------------------------------------------

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Overall Volume by Price - Top 30")
        st.dataframe(volume_by_price_all.head(30), use_container_width=True)

    with col_b:
        st.subheader("Overall Volume by Price × Taker Side - Top 30")
        st.dataframe(side_price_volume_all.head(30), use_container_width=True)

    # -----------------------------------------------------
    # CSV Downloads
    # -----------------------------------------------------

    st.subheader("CSV Downloads")

    dl1, dl2, dl3, dl4 = st.columns(4)

    with dl1:
        st.download_button(
            "Trades CSV",
            df_range.to_csv(index=False).encode("utf-8-sig"),
            file_name="trades.csv",
            mime="text/csv"
        )

    with dl2:
        st.download_button(
            "5m CDV CSV",
            summary_5m.to_csv().encode("utf-8-sig"),
            file_name="5m_cdv_summary.csv",
            mime="text/csv"
        )

    with dl3:
        st.download_button(
            "Volume by Price CSV",
            volume_by_price_all.to_csv(index=False).encode("utf-8-sig"),
            file_name="volume_by_price_all.csv",
            mime="text/csv"
        )

    with dl4:
        st.download_button(
            "Price × Taker Side CSV",
            side_price_volume_all.to_csv().encode("utf-8-sig"),
            file_name="side_price_volume_all.csv",
            mime="text/csv"
        )

    # -----------------------------------------------------
    # Selected 5m Bar Detail Analysis
    # -----------------------------------------------------

    if detail_5m_start_str.strip():
        try:
            detail_start = pd.Timestamp(detail_5m_start_str, tz="Asia/Tokyo")
        except Exception:
            st.error("Invalid selected 5m datetime format. Example: 2026-06-13 20:55:00")
            st.stop()

        detail = analyze_detail_5m(
            df_range=df_range,
            detail_start=detail_start,
            price_round_digit=price_round_digit
        )

        st.subheader("Selected 5m Bar Detail Analysis")

        if detail is None:
            st.warning("No data for the selected 5m bar. Check that it is within the fetched time range.")
        else:
            st.write("Detail Summary")
            st.dataframe(detail["detail_summary"], use_container_width=True)

            detail_tab1, detail_tab2, detail_tab3, detail_tab4, detail_tab5, detail_tab6 = st.tabs([
                "Volume by Price",
                "Price × Taker Side",
                "Volume by Second",
                "Multiple Trades at Same Timestamp",
                "Repeated Same Size Trades",
                "Consecutive Buy/Sell Runs"
            ])

            with detail_tab1:
                st.dataframe(detail["volume_by_price"].head(30), use_container_width=True)

            with detail_tab2:
                st.dataframe(detail["side_price_volume"].head(30), use_container_width=True)

            with detail_tab3:
                st.dataframe(detail["volume_by_second"].head(30), use_container_width=True)

            with detail_tab4:
                st.dataframe(detail["same_time"].head(30), use_container_width=True)

            with detail_tab5:
                st.dataframe(detail["same_size"].head(30), use_container_width=True)

            with detail_tab6:
                st.dataframe(detail["runs"].head(30), use_container_width=True)

            st.subheader("Selected 5m Bar CSV Downloads")

            d1, d2, d3, d4 = st.columns(4)

            with d1:
                st.download_button(
                    "Detail Trades CSV",
                    detail["df_detail"].to_csv(index=False).encode("utf-8-sig"),
                    file_name="detail_trades.csv",
                    mime="text/csv"
                )

            with d2:
                st.download_button(
                    "Detail Summary CSV",
                    detail["detail_summary"].to_csv(index=False).encode("utf-8-sig"),
                    file_name="detail_summary.csv",
                    mime="text/csv"
                )

            with d3:
                st.download_button(
                    "Detail Volume by Price CSV",
                    detail["volume_by_price"].to_csv(index=False).encode("utf-8-sig"),
                    file_name="detail_volume_by_price.csv",
                    mime="text/csv"
                )

            with d4:
                st.download_button(
                    "Detail Volume by Second CSV",
                    detail["volume_by_second"].to_csv().encode("utf-8-sig"),
                    file_name="detail_volume_by_second.csv",
                    mime="text/csv"
                )


# =========================================================
# 実行制御
# =========================================================

if "analysis_data" not in st.session_state:
    st.session_state["analysis_data"] = None

if run:
    tz = "Asia/Tokyo"

    range_end = pd.Timestamp.now(tz=tz)
    range_start = range_end - pd.Timedelta(hours=int(hours_back))

    with st.spinner("Fetching and analyzing Coinbase API data..."):
        df_candles = fetch_coinbase_candles(
            product_id=product_id,
            range_start=range_start,
            range_end=range_end,
            granularity=300
        )

        df_range = fetch_coinbase_trades(
            product_id=product_id,
            range_start=range_start,
            range_end=range_end,
            tz=tz
        )

        if len(df_range) == 0:
            st.error("No trade data was fetched.")
            st.stop()

        summary_5m = make_5m_summary(
            df_range,
            confirm_vol_len=int(confirm_vol_len),
            confirm_vol_mult=float(confirm_vol_mult),
            confirm_lookback=int(confirm_lookback),
            confirm_require_full_window=bool(confirm_require_full_window)
        )
        important_points = detect_important_points(summary_5m)

        latest = summary_5m.tail(1).iloc[0]
        current_price = float(latest["close"])

        volume_by_price_all, side_price_volume_all, sr_levels = calculate_volume_profile_levels(
            df_range=df_range,
            current_price=current_price,
            price_round_digit=price_round_digit,
            top_n=3
        )

        st.session_state["analysis_data"] = {
            "product_id": product_id,
            "range_start": range_start,
            "range_end": range_end,
            "df_candles": df_candles,
            "df_range": df_range,
            "summary_5m": summary_5m,
            "important_points": important_points,
            "volume_by_price_all": volume_by_price_all,
            "side_price_volume_all": side_price_volume_all,
            "sr_levels": sr_levels,
            "confirm_settings": {
                "confirm_vol_len": int(confirm_vol_len),
                "confirm_vol_mult": float(confirm_vol_mult),
                "confirm_lookback": int(confirm_lookback),
                "confirm_require_full_window": bool(confirm_require_full_window),
            },
        }

    st.markdown(
        '<div class="tiny-status">Analysis complete. Point selection does not refetch data.</div>',
        unsafe_allow_html=True
    )

if st.session_state["analysis_data"] is not None:
    render_analysis(st.session_state["analysis_data"])
else:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Ready</div>
            <div class="metric-value">Check the settings on the left and press “Run Analysis”.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
