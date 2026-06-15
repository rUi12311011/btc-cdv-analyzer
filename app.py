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

    /* Streamlit selectbox / BaseWeb layout fix
       The global input CSS can make the hidden select input/caret visible.
       Keep the selected text clean and prevent the fake cursor from appearing. */
    [data-baseweb="select"] {
        width: 100% !important;
        font-size: 12px !important;
    }

    [data-baseweb="select"] > div {
        background-color: #18181b !important;
        border: 1px solid #343438 !important;
        border-radius: 2px !important;
        min-height: 34px !important;
        height: 34px !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: none !important;
    }

    [data-baseweb="select"] input {
        caret-color: transparent !important;
        color: transparent !important;
        background: transparent !important;
        border: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        min-width: 1px !important;
        width: 1px !important;
    }

    [data-baseweb="select"] div {
        color: #e6e2d9 !important;
        font-size: 12px !important;
    }

    [data-baseweb="select"] svg {
        color: #e6e2d9 !important;
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

    /* Streamlit's dataframe already has its own internal border.
       Avoid adding an extra outer frame that creates a double-border look. */
    [data-testid="stDataFrame"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        overflow: visible !important;
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

if "detail_5m_start_str" not in st.session_state:
    st.session_state["detail_5m_start_str"] = "2026-06-13 20:55:00"

if "pending_detail_5m_start_str" in st.session_state:
    st.session_state["detail_5m_start_str"] = st.session_state.pop("pending_detail_5m_start_str")

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

    max_history_hours_raw = st.text_input(
        "Max Historical Hours",
        value="24",
        key="max_history_hours_v2"
    )
    max_history_hours = safe_int_input(max_history_hours_raw, default=24, min_value=1, max_value=168)

    hours_back_raw = st.text_input(
        "Hours Back",
        value="24",
        key="hours_back_v2_force_24h"
    )
    hours_back = safe_int_input(hours_back_raw, default=min(24, max_history_hours), min_value=1, max_value=max_history_hours)

    st.caption(f"取得上限: {max_history_hours}h / 表示対象: {hours_back}h。長くすると取得に時間がかかります。")

    detail_5m_start_str = st.text_input(
        "Selected 5m Bar JST",
        key="detail_5m_start_str"
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
        if st.checkbox("Support", value=True, key="vis_support_candidate"):
            visible_icon_types.append("Support candidate")
        if st.checkbox("Short setup", value=True, key="vis_short_setup"):
            visible_icon_types.append("Short squeeze setup")
        if st.checkbox("Short trigger", value=True, key="vis_short_trigger"):
            visible_icon_types.append("Short squeeze trigger")
        if st.checkbox("Tape sqz", value=True, key="vis_tape_squeeze"):
            visible_icon_types.append("Tape-confirmed squeeze")
        if st.checkbox("Spike risk", value=True, key="vis_spike_risk"):
            visible_icon_types.extend(["Upside spike risk", "Downside spike risk"])
        if st.checkbox("Buy Conf", value=False, key="vis_buy_conf"):
            visible_icon_types.append("Buy confirmation")

    with icon_col2:
        if st.checkbox("Resistance", value=True, key="vis_resistance_candidate"):
            visible_icon_types.append("Resistance candidate")
        if st.checkbox("Long setup", value=True, key="vis_long_setup"):
            visible_icon_types.append("Long squeeze setup")
        if st.checkbox("Long trigger", value=True, key="vis_long_trigger"):
            visible_icon_types.append("Long squeeze trigger")
        if st.checkbox("Thin move", value=True, key="vis_liquidity_thin"):
            visible_icon_types.append("Liquidity thin move")
        if st.checkbox("Sell Conf", value=False, key="vis_sell_conf"):
            visible_icon_types.append("Sell confirmation")

    icon_type_options = [
        "Support candidate",
        "Resistance candidate",
        "Short squeeze setup",
        "Short squeeze trigger",
        "Long squeeze setup",
        "Long squeeze trigger",
        "Tape-confirmed squeeze",
        "Upside spike risk",
        "Downside spike risk",
        "Liquidity thin move",
        "Buy confirmation",
        "Sell confirmation",
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
    st.markdown("### TradingView CSV Baseline")

    tv_csv_files = st.file_uploader(
        "TradingView CSV files",
        type=["csv"],
        accept_multiple_files=True,
        help="確率検証用の母集団。TradingViewの吸収 / Sync / Break履歴CSVをアップロードします。"
    )

    tv_lookahead_bars_raw = st.text_input("TV Lookahead Bars", value="6")
    tv_lookahead_bars = safe_int_input(tv_lookahead_bars_raw, default=6, min_value=1, max_value=100)

    min_squeeze_confidence_raw = st.text_input("Min Squeeze Confidence %", value="50")
    min_squeeze_confidence = safe_float_input(min_squeeze_confidence_raw, default=50.0, min_value=0.0, max_value=100.0)

    max_squeeze_icons_raw = st.text_input("Max Squeeze Icons / Type", value="4")
    max_squeeze_icons = safe_int_input(max_squeeze_icons_raw, default=4, min_value=1, max_value=50)

    liquidity_keep_pct_raw = st.text_input("Liquidity Thin Keep %", value="33")
    liquidity_keep_pct = safe_float_input(liquidity_keep_pct_raw, default=33.0, min_value=1.0, max_value=100.0)

    hide_low_confidence_points = st.checkbox(
        "Filter chart points",
        value=True,
        help="スクイーズ系は種類ごとに上位を残し、Liquidity thin moveは確度/スコア上位だけ残します。"
    )

    st.caption("TV CSV = 構造検証・母集団 / Coinbase tape = テープ確認。TV CSVだけでTape-confirmedとは断定しません。")

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
    """Coinbase candlesを取得する。

    Coinbaseのcandles APIは1回あたり最大約300本のため、24時間を超える場合でも
    5分足を分割取得してチャートが途中で切れないようにする。
    """
    url = f"https://api.exchange.coinbase.com/products/{product_id}/candles"

    max_candles_per_request = 300
    chunk_seconds = granularity * max_candles_per_request
    chunk_delta = pd.Timedelta(seconds=chunk_seconds)

    all_frames = []
    cur_start = range_start
    request_count = 0

    while cur_start < range_end:
        cur_end = min(cur_start + chunk_delta, range_end)
        params = {
            "start": cur_start.tz_convert("UTC").isoformat(),
            "end": cur_end.tz_convert("UTC").isoformat(),
            "granularity": granularity
        }

        res = requests.get(url, params=params)

        if res.status_code != 200:
            st.error(f"ローソク足APIエラー: {res.status_code}")
            st.write(res.text)
            break

        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            df_part = pd.DataFrame(
                data,
                columns=["time", "low", "high", "open", "close", "volume"]
            )
            df_part["time"] = pd.to_datetime(df_part["time"], unit="s", utc=True).dt.tz_convert("Asia/Tokyo")
            all_frames.append(df_part)

        request_count += 1
        cur_start = cur_end
        time.sleep(0.05)

    if not all_frames:
        return pd.DataFrame()

    df = pd.concat(all_frames, ignore_index=True)
    df = df.drop_duplicates(subset=["time"]).sort_values("time")

    # 取得範囲の外側を念のため除外
    df = df[(df["time"] >= range_start) & (df["time"] <= range_end)].copy()

    return df


# =========================================================
# ローソク足チャート表示
# =========================================================

def show_candlestick_chart(df_candles, product_id, important_points=None, selected_point=None, sr_levels=None, legend_types=None):
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
            "Sell confirmation": "line-ew",
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

        marker_colors.update({
            "Support candidate": "#111111",
            "Resistance candidate": "#111111",
            "Short squeeze setup": "#c1121f",
            "Short squeeze trigger": "#c1121f",
            "Long squeeze setup": "#c1121f",
            "Long squeeze trigger": "#c1121f",
            "Tape-confirmed squeeze": "#c1121f",
            "Liquidity thin move": "#4f4f4f",
            "Upside spike risk": "#c1121f",
            "Downside spike risk": "#c1121f",
            "Failed breakout": "#8f0d17",
        })
        marker_symbols.update({
            "Support candidate": "triangle-up-open",
            "Resistance candidate": "triangle-down-open",
            "Short squeeze setup": "star-open",
            "Short squeeze trigger": "star",
            "Long squeeze setup": "asterisk-open",
            "Long squeeze trigger": "asterisk",
            "Tape-confirmed squeeze": "star-diamond",
            "Liquidity thin move": "diamond-open",
            "Upside spike risk": "arrow-up",
            "Downside spike risk": "arrow-down",
            "Failed breakout": "x",
        })
        marker_line_colors.update({
            "Support candidate": "#111111",
            "Resistance candidate": "#111111",
            "Short squeeze setup": "#c1121f",
            "Short squeeze trigger": "#c1121f",
            "Long squeeze setup": "#c1121f",
            "Long squeeze trigger": "#c1121f",
            "Tape-confirmed squeeze": "#c1121f",
            "Liquidity thin move": "#4f4f4f",
            "Upside spike risk": "#c1121f",
            "Downside spike risk": "#c1121f",
            "Failed breakout": "#8f0d17",
        })
        marker_sizes.update({
            "Support candidate": 13,
            "Resistance candidate": 13,
            "Short squeeze setup": 14,
            "Short squeeze trigger": 16,
            "Long squeeze setup": 14,
            "Long squeeze trigger": 16,
            "Tape-confirmed squeeze": 17,
            "Liquidity thin move": 12,
            "Upside spike risk": 17,
            "Downside spike risk": 17,
            "Failed breakout": 13,
        })
        marker_line_widths.update({
            "Support candidate": 1.3,
            "Resistance candidate": 1.3,
            "Short squeeze setup": 1.4,
            "Short squeeze trigger": 1.6,
            "Long squeeze setup": 1.4,
            "Long squeeze trigger": 1.6,
            "Tape-confirmed squeeze": 1.7,
            "Liquidity thin move": 1.2,
            "Upside spike risk": 1.8,
            "Downside spike risk": 1.8,
            "Failed breakout": 1.5,
        })

        plotted_point_types = set()

        for point_type, group in important_points.groupby("type"):
            plotted_point_types.add(point_type)
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

        # Keep legend icons visible even when the current data has no point for that type.
        # This avoids the impression that a symbol disappeared.
        if legend_types is not None:
            for point_type in legend_types:
                if point_type not in plotted_point_types and point_type in marker_symbols:
                    fig.add_trace(
                        go.Scatter(
                            x=[None],
                            y=[None],
                            mode="markers",
                            marker=dict(
                                size=marker_sizes.get(point_type, 13),
                                color=marker_colors.get(point_type, "#111111"),
                                symbol=marker_symbols.get(point_type, "circle"),
                                line=dict(width=marker_line_widths.get(point_type, 1.3), color=marker_line_colors.get(point_type, "#111111"))
                            ),
                            name=point_type,
                            hoverinfo="skip",
                            showlegend=True
                        ),
                        row=1,
                        col=1
                    )

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
        margin=dict(l=20, r=250, t=12, b=50),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(170, 170, 170, 0.92)",
            bordercolor="#111111",
            borderwidth=1,
            font=dict(size=10, color="#111111"),
            itemwidth=30,
            tracegroupgap=2,
            itemsizing="constant"
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

    def _max_same_side_streak(side_series):
        max_run = 0
        current_run = 0
        prev_side = None
        for side in side_series.astype(str).tolist():
            if side == prev_side:
                current_run += 1
            else:
                current_run = 1
                prev_side = side
            max_run = max(max_run, current_run)
        return max_run

    same_side_streak = grouped["taker_side_estimate"].apply(_max_same_side_streak)
    summary_5m["same_side_streak"] = same_side_streak.fillna(0).astype(int)

    large_trade_threshold = df_range["size_BTC"].quantile(0.95) if len(df_range) > 0 else 0
    large_trade_counts = (
        df_range[df_range["size_BTC"] >= large_trade_threshold]
        .groupby("time_5m")["size_BTC"]
        .count()
    )
    summary_5m["large_trade_count"] = large_trade_counts.reindex(summary_5m.index).fillna(0).astype(int)
    summary_5m["trade_velocity_per_min"] = summary_5m["trade_count"] / 5.0

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
    summary_5m["price_impact_per_BTC"] = summary_5m["body_abs"] / summary_5m["volume_BTC"].replace(0, pd.NA)
    summary_5m["delta_impact_score"] = summary_5m["body_abs"] / summary_5m["delta_abs"].replace(0, pd.NA)
    impact_rank = summary_5m["price_impact_per_BTC"].rank(pct=True).fillna(0)
    summary_5m["liquidity_thin_score"] = (impact_rank * 100).round(1)

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
            "memo": "現在値より下にある出来高集中帯。Support候補。"
        })

    for _, r in resistances.iterrows():
        levels.append({
            "kind": "Resistance",
            "price": float(r["price_bin"]),
            "volume_BTC": float(r["size_BTC"]),
            "distance_from_current": float(r["price_bin"] - current_price),
            "memo": "現在値より上にある出来高集中帯。Resistance候補。"
        })

    sr_levels = pd.DataFrame(levels)
    sr_levels = sr_levels.drop_duplicates(subset=["kind", "price"])

    return volume_by_price_all, side_price_volume_all, sr_levels



# =========================================================
# TradingView CSV 確率検証ベースライン
# =========================================================

def _tv_bool_signal(df, candidate_cols):
    """TradingView CSVのplot/plotshape列をbool化する。列が無ければFalse。"""
    sig = pd.Series(False, index=df.index)
    for col in candidate_cols:
        if col in df.columns:
            vals = pd.to_numeric(df[col], errors="coerce").fillna(0)
            sig = sig | (vals != 0)
    return sig


def _normalize_tv_csv(uploaded_file):
    """TradingView CSVを確率検証用に標準化する。"""
    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file)
    df.columns = [str(c).strip() for c in df.columns]

    # TradingView CSVは time がUNIX秒のことが多い。文字列日時にも一応対応。
    if "time" in df.columns:
        raw_time = df["time"]
        numeric_time = pd.to_numeric(raw_time, errors="coerce")
        if numeric_time.notna().mean() > 0.8:
            df["time_jst"] = pd.to_datetime(numeric_time, unit="s", utc=True).dt.tz_convert("Asia/Tokyo")
        else:
            df["time_jst"] = pd.to_datetime(raw_time, errors="coerce", utc=True).dt.tz_convert("Asia/Tokyo")
    else:
        df["time_jst"] = pd.NaT

    for col in ["open", "high", "low", "close", "Volume", "ATR"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 列名はTradingViewエクスポートで微妙に変わることがあるため候補を広めに見る。
    df["tv_sell_absorption"] = _tv_bool_signal(df, [
        "Sell Absorption XL", "Sell Absorption L", "Sell Absorption M", "Sell Absorption S",
        "Sell Absorption", "sellAbsorption"
    ])
    df["tv_buy_absorption"] = _tv_bool_signal(df, [
        "Buy Absorption XL", "Buy Absorption L", "Buy Absorption M", "Buy Absorption S",
        "Buy Absorption", "buyAbsorption"
    ])
    df["tv_bull_sync"] = _tv_bool_signal(df, ["Bull Sync", "bullSync"])
    df["tv_bear_sync"] = _tv_bool_signal(df, ["Bear Sync", "bearSync"])
    df["tv_liquidity_thin"] = _tv_bool_signal(df, ["Liquidity Thin", "liquidityThin"])
    df["tv_break_up"] = _tv_bool_signal(df, ["Break Up", "breakUpConfirmed"])
    df["tv_break_down"] = _tv_bool_signal(df, ["Break Down", "breakDownConfirmed"])
    df["tv_long_score"] = _tv_bool_signal(df, ["LONG Score Label", "LONG Entry Score", "L5+"])
    df["tv_short_score"] = _tv_bool_signal(df, ["SHORT Score Label", "SHORT Entry Score", "S5+"])

    return df


def analyze_tradingview_probability(tv_csv_files, lookahead_bars=6):
    """TradingView CSVから、吸収がブレイク/維持に発展した割合を作る。

    これは構造上のHistorical Probabilityであり、Tape-confirmed判定ではない。
    """
    if not tv_csv_files:
        return {
            "stats_table": pd.DataFrame(),
            "events_table": pd.DataFrame(),
            "lookup": {},
            "source_count": 0,
            "note": "TradingView CSV未入力"
        }

    all_events = []
    source_names = []

    for f in tv_csv_files:
        try:
            df = _normalize_tv_csv(f)
        except Exception as e:
            st.warning(f"TradingView CSV読み込み失敗: {getattr(f, 'name', 'unknown')} / {e}")
            continue

        if len(df) == 0 or not {"open", "high", "low", "close"}.issubset(df.columns):
            st.warning(f"TradingView CSVにOHLC列が不足しています: {getattr(f, 'name', 'unknown')}")
            continue

        df = df.reset_index(drop=True)
        source_name = getattr(f, "name", "uploaded_csv")
        source_names.append(source_name)

        for i, row in df.iterrows():
            future = df.iloc[i+1:i+1+int(lookahead_bars)]
            if len(future) == 0:
                continue

            high = float(row["high"])
            low = float(row["low"])
            close = float(row["close"])
            rng = max(high - low, 0.0)
            atr = float(row["ATR"]) if "ATR" in df.columns and pd.notna(row.get("ATR", pd.NA)) else rng
            # 銘柄/時間足に依存しすぎないよう、最低幅は設けず足レンジ/ATR基準で見る。
            break_buffer = max(rng * 0.03, atr * 0.02, 0.0)

            # sell absorption = 成行売りが吸収された可能性。Support候補/Short squeeze構造の母集団。
            if bool(row.get("tv_sell_absorption", False)):
                outcome = "support_hold"
                trigger_time = pd.NaT
                trigger_close = pd.NA
                evidence = "吸収後、Lookahead内で明確なブレイクなし。"
                for _, fut in future.iterrows():
                    if float(fut["close"]) > high + break_buffer:
                        trigger_time = fut.get("time_jst", pd.NaT)
                        trigger_close = float(fut["close"])
                        if bool(fut.get("tv_bull_sync", False)) or bool(fut.get("tv_break_up", False)) or bool(fut.get("tv_long_score", False)):
                            outcome = "short_squeeze_proxy"
                            evidence = "sell吸収後に高値上抜け + Bull Sync/Break Up/LONG Score。"
                        else:
                            outcome = "up_break_without_sync"
                            evidence = "sell吸収後に高値上抜け。ただしSync/Break確認は弱い。"
                        break
                    if float(fut["close"]) < low - break_buffer:
                        trigger_time = fut.get("time_jst", pd.NaT)
                        trigger_close = float(fut["close"])
                        outcome = "support_failed"
                        evidence = "sell吸収後に安値を下抜け。Support候補失敗。"
                        break

                all_events.append({
                    "source_file": source_name,
                    "time_jst": row.get("time_jst", pd.NaT),
                    "setup_type": "Short squeeze setup / Support candidate",
                    "absorption_kind": "sell_absorption",
                    "absorption_high": high,
                    "absorption_low": low,
                    "close": close,
                    "outcome": outcome,
                    "trigger_time_jst": trigger_time,
                    "trigger_close": trigger_close,
                    "lookahead_bars": int(lookahead_bars),
                    "evidence": evidence,
                })

            # buy absorption = 成行買いが吸収された可能性。Resistance候補/Long squeeze構造の母集団。
            if bool(row.get("tv_buy_absorption", False)):
                outcome = "resistance_hold"
                trigger_time = pd.NaT
                trigger_close = pd.NA
                evidence = "吸収後、Lookahead内で明確なブレイクなし。"
                for _, fut in future.iterrows():
                    if float(fut["close"]) < low - break_buffer:
                        trigger_time = fut.get("time_jst", pd.NaT)
                        trigger_close = float(fut["close"])
                        if bool(fut.get("tv_bear_sync", False)) or bool(fut.get("tv_break_down", False)) or bool(fut.get("tv_short_score", False)):
                            outcome = "long_squeeze_proxy"
                            evidence = "buy吸収後に安値下抜け + Bear Sync/Break Down/SHORT Score。"
                        else:
                            outcome = "down_break_without_sync"
                            evidence = "buy吸収後に安値下抜け。ただしSync/Break確認は弱い。"
                        break
                    if float(fut["close"]) > high + break_buffer:
                        trigger_time = fut.get("time_jst", pd.NaT)
                        trigger_close = float(fut["close"])
                        outcome = "resistance_failed"
                        evidence = "buy吸収後に高値を上抜け。Resistance候補失敗。"
                        break

                all_events.append({
                    "source_file": source_name,
                    "time_jst": row.get("time_jst", pd.NaT),
                    "setup_type": "Long squeeze setup / Resistance candidate",
                    "absorption_kind": "buy_absorption",
                    "absorption_high": high,
                    "absorption_low": low,
                    "close": close,
                    "outcome": outcome,
                    "trigger_time_jst": trigger_time,
                    "trigger_close": trigger_close,
                    "lookahead_bars": int(lookahead_bars),
                    "evidence": evidence,
                })

    events = pd.DataFrame(all_events)
    if len(events) == 0:
        return {
            "stats_table": pd.DataFrame(),
            "events_table": events,
            "lookup": {},
            "source_count": len(source_names),
            "note": "吸収イベントが見つかりませんでした。"
        }

    stats_rows = []
    lookup = {}
    groups = {
        "short_squeeze_setup": {
            "label": "Short squeeze setup / Support candidate",
            "squeeze_outcome": "short_squeeze_proxy",
            "hold_outcome": "support_hold",
            "failed_outcome": "support_failed",
        },
        "long_squeeze_setup": {
            "label": "Long squeeze setup / Resistance candidate",
            "squeeze_outcome": "long_squeeze_proxy",
            "hold_outcome": "resistance_hold",
            "failed_outcome": "resistance_failed",
        },
    }

    for key, cfg in groups.items():
        sub = events[events["setup_type"] == cfg["label"]]
        total = len(sub)
        if total == 0:
            prob = pd.NA
            hold = pd.NA
            failed = pd.NA
            break_any = pd.NA
        else:
            squeeze_count = int((sub["outcome"] == cfg["squeeze_outcome"]).sum())
            hold_count = int((sub["outcome"] == cfg["hold_outcome"]).sum())
            failed_count = int((sub["outcome"] == cfg["failed_outcome"]).sum())
            break_count = int(sub["outcome"].isin([
                cfg["squeeze_outcome"], "up_break_without_sync", "down_break_without_sync"
            ]).sum())
            prob = squeeze_count / total * 100
            hold = hold_count / total * 100
            failed = failed_count / total * 100
            break_any = break_count / total * 100
            lookup[key] = prob

        stats_rows.append({
            "setup_key": key,
            "setup_type": cfg["label"],
            "total_setups": total,
            "squeeze_proxy_%": round(prob, 1) if pd.notna(prob) else pd.NA,
            "any_break_%": round(break_any, 1) if pd.notna(break_any) else pd.NA,
            "support_or_resistance_hold_%": round(hold, 1) if pd.notna(hold) else pd.NA,
            "failed_%": round(failed, 1) if pd.notna(failed) else pd.NA,
            "lookahead_bars": int(lookahead_bars),
            "source_files": len(set(events["source_file"])),
            "note": "TradingView構造CSV由来。Tape-confirmedではない。"
        })

    stats = pd.DataFrame(stats_rows)
    return {
        "stats_table": stats,
        "events_table": events,
        "lookup": lookup,
        "source_count": len(source_names),
        "note": "Historical Probability = TradingView CSVの構造検証。Coinbase tape確認とは別。"
    }


# =========================================================
# 重要ポイント自動抽出
# =========================================================

def detect_important_points(summary_5m, tv_probability_stats=None):
    """Absorption-first classifier.

    This app is not an entry engine. It classifies whether an absorption area later behaves as
    support/resistance, squeeze setup, squeeze trigger, or tape-confirmed squeeze.
    """
    rows = []

    if summary_5m is None or len(summary_5m) == 0:
        return pd.DataFrame()

    historical_lookup = {}
    if isinstance(tv_probability_stats, dict):
        historical_lookup = tv_probability_stats.get("lookup", {}) or {}

    def hist_prob_for(point_type):
        if point_type in ["Short squeeze setup", "Short squeeze trigger", "Tape-confirmed squeeze"]:
            return historical_lookup.get("short_squeeze_setup", pd.NA)
        if point_type in ["Long squeeze setup", "Long squeeze trigger"]:
            return historical_lookup.get("long_squeeze_setup", pd.NA)
        return pd.NA

    def blend_confidence(current_confidence, hist_prob):
        try:
            if pd.isna(hist_prob):
                return float(current_confidence)
            # 現在のテープ/構造スコアを主、TV母集団の実測値を補助として合成。
            return float(current_confidence) * 0.65 + float(hist_prob) * 0.35
        except Exception:
            return float(current_confidence)

    df = summary_5m.copy().reset_index()
    vol_threshold = df["volume_BTC"].quantile(0.80)
    thin_threshold = df["liquidity_thin_score"].quantile(0.70) if "liquidity_thin_score" in df.columns else 70

    def safe_float(v, default=0.0):
        try:
            if pd.isna(v):
                return default
            return float(v)
        except Exception:
            return default

    def base_from_row(row):
        return {
            "time_5m": row["time_5m"],
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
            "delta_strength": row.get("delta_strength", pd.NA),
            "price_not_moved": row.get("price_not_moved", False),
            "confirm_vol_avg": row.get("confirm_vol_avg", pd.NA),
            "confirm_vol_mult_actual": row.get("confirm_vol_mult_actual", pd.NA),
            "confirm_volume_ok": row.get("confirm_volume_ok", False),
            "same_side_streak": int(row.get("same_side_streak", 0)),
            "large_trade_count": int(row.get("large_trade_count", 0)),
            "price_impact_per_BTC": safe_float(row.get("price_impact_per_BTC", 0)),
            "liquidity_thin_score": safe_float(row.get("liquidity_thin_score", 0)),
            "delta_impact_score": safe_float(row.get("delta_impact_score", 0)),
        }

    def add_point(row, point_type, score, reason, absorption_high=pd.NA, absorption_low=pd.NA,
                  break_level=pd.NA, invalid_level=pd.NA, status="", tape_score=0,
                  squeeze_confidence=0, memo="", spot_price=None):
        base = base_from_row(row)
        if spot_price is not None:
            base["spot_price"] = spot_price
        historical_probability = hist_prob_for(point_type)
        adjusted_confidence = blend_confidence(squeeze_confidence, historical_probability)
        base.update({
            "type": point_type,
            "score": round(float(score), 1),
            "reason": reason,
            "absorption_high": absorption_high,
            "absorption_low": absorption_low,
            "break_level": break_level,
            "invalid_level": invalid_level,
            "support_or_resistance_status": status,
            "tape_score": round(float(tape_score), 1),
            "squeeze_confidence": round(float(adjusted_confidence), 1),
            "historical_probability_%": round(float(historical_probability), 1) if pd.notna(historical_probability) else pd.NA,
            "memo": memo,
        })
        rows.append(base)

    def tape_score_for(row, direction):
        # direction: "up" for short squeeze, "down" for long squeeze
        if direction == "up":
            side_ratio = safe_float(row.get("buy_ratio_%", 0))
            delta_ok = row.get("delta_BTC", 0) > 0
            price_ok = row.get("candle_move", 0) > 0
        else:
            side_ratio = safe_float(row.get("sell_ratio_%", 0))
            delta_ok = row.get("delta_BTC", 0) < 0
            price_ok = row.get("candle_move", 0) < 0

        score = 0
        score += min(30, max(0, side_ratio - 50) * 1.5)
        score += min(20, safe_float(row.get("same_side_streak", 0)) * 2.0)
        score += min(15, safe_float(row.get("large_trade_count", 0)) * 3.0)
        score += min(20, safe_float(row.get("liquidity_thin_score", 0)) * 0.20)
        score += 10 if delta_ok else 0
        score += 5 if price_ok else 0
        return min(100, score)

    lookahead = 6

    for i, row in df.iterrows():
        future = df.iloc[i+1:i+1+lookahead]

        # sell delta absorbed: sell came in, price did not fall. This can become support or short squeeze setup.
        if bool(row.get("buy_absorption_candidate", False)):
            absorption_high = row["high"]
            absorption_low = row["low"]
            break_buffer = max(float(row.get("range", 0)) * 0.03, 5.0)
            future_up = future[
                (future["close"] > absorption_high + break_buffer) &
                (future["delta_BTC"] > 0) &
                (future["buy_ratio_%"] >= 55) &
                (future["candle_move"] > 0)
            ]
            future_down = future[
                (future["close"] < absorption_low - break_buffer) &
                (future["delta_BTC"] < 0) &
                (future["sell_ratio_%"] >= 55) &
                (future["candle_move"] < 0)
            ]

            setup_tape = tape_score_for(row, "up")
            setup_confidence = min(75, 35 + setup_tape * 0.35)
            add_point(
                row,
                "Short squeeze setup",
                score=82,
                reason=(
                    f"sell吸収を確認。sell delta {row['delta_BTC']:.2f} BTC に対して価格が下に進んでいない。"
                    f"吸収足高値 {absorption_high:.2f} を明確に上抜け、かつbuy delta優勢ならShort squeeze trigger候補。"
                ),
                absorption_high=absorption_high,
                absorption_low=absorption_low,
                break_level=absorption_high,
                invalid_level=absorption_low,
                status="Short squeeze setup / waiting for absorption high break",
                tape_score=setup_tape,
                squeeze_confidence=setup_confidence,
                memo="このアイコンはスクイーズ予兆。自動でSelected 5m Bar JSTへ送る対象。",
                spot_price=row["high"]
            )

            if len(future_up) > 0:
                trigger = future_up.iloc[0]
                tape = tape_score_for(trigger, "up")
                confidence = 55 + min(35, tape * 0.35)
                point_type = "Tape-confirmed squeeze" if tape >= 70 else "Short squeeze trigger"
                add_point(
                    trigger,
                    point_type,
                    score=90 if tape >= 70 else 84,
                    reason=(
                        f"{row['time_5m']} のsell吸収後、吸収足高値 {absorption_high:.2f} を上抜け。"
                        f"buy比率 {trigger['buy_ratio_%']:.1f}%、delta {trigger['delta_BTC']:.2f} BTC、"
                        f"tape_score {tape:.1f}。ショートが踏まれ始めた可能性。"
                    ),
                    absorption_high=absorption_high,
                    absorption_low=absorption_low,
                    break_level=absorption_high,
                    invalid_level=absorption_low,
                    status="吸収高値を上抜け。Short squeeze trigger。",
                    tape_score=tape,
                    squeeze_confidence=confidence,
                    memo="sell吸収を起点に上方向へブレイク。テープ確認でスクイーズ確度を評価。",
                    spot_price=trigger["close"]
                )
            elif len(future_down) > 0:
                fail = future_down.iloc[0]
                tape = tape_score_for(fail, "down")
                confidence = min(95, 58 + tape * 0.35 + min(10, safe_float(fail.get("liquidity_thin_score", 0)) * 0.08))
                add_point(
                    fail,
                    "Downside spike risk",
                    score=86,
                    reason=(
                        f"{row['time_5m']} のsell吸収＝Support候補が失敗。"
                        f"吸収足安値 {absorption_low:.2f} を下抜け、sell比率 {fail['sell_ratio_%']:.1f}%、"
                        f"delta {fail['delta_BTC']:.2f} BTC、liquidity_thin_score {safe_float(fail.get('liquidity_thin_score', 0)):.1f}。"
                        f"下方向のStop-run / Spike risk。"
                    ),
                    absorption_high=absorption_high,
                    absorption_low=absorption_low,
                    break_level=absorption_low,
                    invalid_level=absorption_high,
                    status="Support failed / downside spike risk",
                    tape_score=tape,
                    squeeze_confidence=confidence,
                    memo="吸収が支えにならず逆方向に抜けた。単なるFailed breakoutではなく、流動性が薄い方向へのスパイク警戒。",
                    spot_price=fail["close"]
                )
            else:
                add_point(
                    row,
                    "Support candidate",
                    score=78 + min(15, safe_float(row.get("delta_strength", 0)) * 30),
                    reason=(
                        f"sell delta {row['delta_BTC']:.2f} BTC に対して実体 {row['candle_move']:.2f} USD。"
                        f"sellが出ているのに下方向へ十分進まず、吸収足安値 {absorption_low:.2f} がSupport候補。"
                    ),
                    absorption_high=absorption_high,
                    absorption_low=absorption_low,
                    break_level=absorption_high,
                    invalid_level=absorption_low,
                    status="Support candidate / Short squeeze setup waiting",
                    tape_score=tape_score_for(row, "up"),
                    squeeze_confidence=35,
                    memo="吸収足高値を上抜ければShort squeeze setup、安値割れならSupport失敗。",
                    spot_price=row["low"]
                )

        # buy delta absorbed: buy came in, price did not rise. This can become resistance or long squeeze setup.
        if bool(row.get("sell_absorption_candidate", False)):
            absorption_high = row["high"]
            absorption_low = row["low"]
            break_buffer = max(float(row.get("range", 0)) * 0.03, 5.0)
            future_down = future[
                (future["close"] < absorption_low - break_buffer) &
                (future["delta_BTC"] < 0) &
                (future["sell_ratio_%"] >= 55) &
                (future["candle_move"] < 0)
            ]
            future_up = future[
                (future["close"] > absorption_high + break_buffer) &
                (future["delta_BTC"] > 0) &
                (future["buy_ratio_%"] >= 55) &
                (future["candle_move"] > 0)
            ]

            setup_tape = tape_score_for(row, "down")
            setup_confidence = min(75, 35 + setup_tape * 0.35)
            add_point(
                row,
                "Long squeeze setup",
                score=82,
                reason=(
                    f"buy吸収を確認。buy delta +{row['delta_BTC']:.2f} BTC に対して価格が上に進んでいない。"
                    f"吸収足安値 {absorption_low:.2f} を明確に下抜け、かつsell delta優勢ならLong squeeze trigger候補。"
                ),
                absorption_high=absorption_high,
                absorption_low=absorption_low,
                break_level=absorption_low,
                invalid_level=absorption_high,
                status="Long squeeze setup / waiting for absorption low break",
                tape_score=setup_tape,
                squeeze_confidence=setup_confidence,
                memo="このアイコンはスクイーズ予兆。自動でSelected 5m Bar JSTへ送る対象。",
                spot_price=row["low"]
            )

            if len(future_down) > 0:
                trigger = future_down.iloc[0]
                tape = tape_score_for(trigger, "down")
                confidence = 55 + min(35, tape * 0.35)
                point_type = "Tape-confirmed squeeze" if tape >= 70 else "Long squeeze trigger"
                add_point(
                    trigger,
                    point_type,
                    score=90 if tape >= 70 else 84,
                    reason=(
                        f"{row['time_5m']} のbuy吸収後、吸収足安値 {absorption_low:.2f} を下抜け。"
                        f"sell比率 {trigger['sell_ratio_%']:.1f}%、delta {trigger['delta_BTC']:.2f} BTC、"
                        f"tape_score {tape:.1f}。ロングが投げ始めた可能性。"
                    ),
                    absorption_high=absorption_high,
                    absorption_low=absorption_low,
                    break_level=absorption_low,
                    invalid_level=absorption_high,
                    status="吸収安値を下抜け。Long squeeze trigger。",
                    tape_score=tape,
                    squeeze_confidence=confidence,
                    memo="buy吸収を起点に下方向へブレイク。テープ確認でスクイーズ確度を評価。",
                    spot_price=trigger["close"]
                )
            elif len(future_up) > 0:
                fail = future_up.iloc[0]
                tape = tape_score_for(fail, "up")
                confidence = min(95, 58 + tape * 0.35 + min(10, safe_float(fail.get("liquidity_thin_score", 0)) * 0.08))
                add_point(
                    fail,
                    "Upside spike risk",
                    score=86,
                    reason=(
                        f"{row['time_5m']} のbuy吸収＝Resistance候補が失敗。"
                        f"吸収足高値 {absorption_high:.2f} を上抜け、buy比率 {fail['buy_ratio_%']:.1f}%、"
                        f"delta {fail['delta_BTC']:.2f} BTC、liquidity_thin_score {safe_float(fail.get('liquidity_thin_score', 0)):.1f}。"
                        f"上方向のStop-run / Spike risk。"
                    ),
                    absorption_high=absorption_high,
                    absorption_low=absorption_low,
                    break_level=absorption_high,
                    invalid_level=absorption_low,
                    status="Resistance failed / upside spike risk",
                    tape_score=tape,
                    squeeze_confidence=confidence,
                    memo="吸収が抵抗にならず逆方向に抜けた。単なるFailed breakoutではなく、流動性が薄い方向へのスパイク警戒。",
                    spot_price=fail["close"]
                )
            else:
                add_point(
                    row,
                    "Resistance candidate",
                    score=78 + min(15, safe_float(row.get("delta_strength", 0)) * 30),
                    reason=(
                        f"buy delta +{row['delta_BTC']:.2f} BTC に対して実体 {row['candle_move']:.2f} USD。"
                        f"buyが出ているのに上方向へ十分進まず、吸収足高値 {absorption_high:.2f} がResistance候補。"
                    ),
                    absorption_high=absorption_high,
                    absorption_low=absorption_low,
                    break_level=absorption_low,
                    invalid_level=absorption_high,
                    status="Resistance candidate / Long squeeze setup waiting",
                    tape_score=tape_score_for(row, "down"),
                    squeeze_confidence=35,
                    memo="吸収足安値を下抜ければLong squeeze setup、高値上抜けならResistance失敗。",
                    spot_price=row["high"]
                )

        if bool(row.get("bullish_confirmation", False)):
            add_point(
                row,
                "Buy confirmation",
                score=72,
                reason=f"出来高急増後、価格とCVDが上方向に同期。delta {row['delta_BTC']:.2f} BTC、値幅 {row['candle_move']:.2f} USD。",
                status="Bull sync confirmation",
                tape_score=tape_score_for(row, "up"),
                squeeze_confidence=0,
                memo="単体ではスクイーズではない。直前の吸収ブレイクと組み合わせて評価。",
                spot_price=row["low"] - max(row.get("range", 0) * 0.20, 8)
            )

        if bool(row.get("bearish_confirmation", False)):
            add_point(
                row,
                "Sell confirmation",
                score=72,
                reason=f"出来高急増後、価格とCVDが下方向に同期。delta {row['delta_BTC']:.2f} BTC、値幅 {row['candle_move']:.2f} USD。",
                status="Bear sync confirmation",
                tape_score=tape_score_for(row, "down"),
                squeeze_confidence=0,
                memo="単体ではスクイーズではない。直前の吸収ブレイクと組み合わせて評価。",
                spot_price=row["high"] + max(row.get("range", 0) * 0.20, 8)
            )

        if safe_float(row.get("liquidity_thin_score", 0)) >= thin_threshold and row["volume_BTC"] < vol_threshold:
            add_point(
                row,
                "Liquidity thin move",
                score=62,
                reason=(
                    f"少ない出来高に対して価格インパクトが大きい。"
                    f"impact_per_BTC {safe_float(row.get('price_impact_per_BTC', 0)):.2f}、"
                    f"liquidity_thin_score {safe_float(row.get('liquidity_thin_score', 0)):.1f}。"
                ),
                status="Liquidity thin / not squeeze by itself",
                tape_score=max(tape_score_for(row, "up"), tape_score_for(row, "down")),
                squeeze_confidence=0,
                memo="流動性が薄い可能性。吸収起点のブレイクと重なる場合のみスクイーズ材料。",
                spot_price=row["close"]
            )

    if not rows:
        return pd.DataFrame()

    points = pd.DataFrame(rows)
    points = points.drop_duplicates(subset=["time_5m", "type", "absorption_high", "absorption_low"])
    points = points.sort_values(["score", "tape_score", "volume_BTC"], ascending=False).reset_index(drop=True)

    points["No"] = range(1, len(points) + 1)
    points["point_id"] = points.apply(
        lambda r: f"{r['time_5m'].isoformat()}__{r['type']}__{r['No']}",
        axis=1
    )
    points["label"] = points.apply(
        lambda r: f"{int(r['No'])}. {r['time_5m'].strftime('%m/%d %H:%M')} | {r['type']} | score {r['score']} | close {r['close']:.2f}",
        axis=1
    )

    points["icon_side"] = points["candle_move"].apply(lambda x: "below" if x < 0 else "above")
    points = points.sort_values(["time_5m", "icon_side", "score"], ascending=[True, True, False]).reset_index(drop=True)
    points["icon_slot"] = points.groupby(["time_5m", "icon_side"]).cumcount()

    def _icon_y(r):
        row_range = r["high"] - r["low"]
        pad = max(row_range * 0.22, 18)
        step = max(row_range * 0.16, 12)
        if r["icon_side"] == "below":
            return r["low"] - pad - r["icon_slot"] * step
        return r["high"] + pad + r["icon_slot"] * step

    points["icon_y"] = points.apply(_icon_y, axis=1)

    return points


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
    tv_probability_stats = data.get("tv_probability_stats", {}) or {}

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

    requested_hours_back = data.get("requested_hours_back", None)
    max_history_hours = data.get("max_history_hours", None)
    actual_candle_hours = None
    try:
        if df_candles is not None and len(df_candles) > 1:
            actual_candle_hours = (df_candles["time"].max() - df_candles["time"].min()).total_seconds() / 3600
    except Exception:
        actual_candle_hours = None

    extra_range_note = ""
    if requested_hours_back is not None:
        extra_range_note = f" / requested {requested_hours_back}h"
    if actual_candle_hours is not None:
        extra_range_note += f" / chart span {actual_candle_hours:.1f}h"

    st.markdown(
        f'<div class="tiny-status">Data: {range_start.strftime("%Y-%m-%d %H:%M")} – {range_end.strftime("%Y-%m-%d %H:%M")}{extra_range_note}</div>',
        unsafe_allow_html=True
    )

    # TradingView CSVの構造検証ベースライン。Tape-confirmedとは別枠で表示する。
    stats_table = tv_probability_stats.get("stats_table", pd.DataFrame()) if isinstance(tv_probability_stats, dict) else pd.DataFrame()
    events_table = tv_probability_stats.get("events_table", pd.DataFrame()) if isinstance(tv_probability_stats, dict) else pd.DataFrame()
    if stats_table is not None and len(stats_table) > 0:
        st.subheader("TradingView CSV Probability Baseline")
        st.caption("Historical ProbabilityはTradingView CSV由来の構造確率です。Coinbase tapeによるTape-confirmed判定ではありません。")
        st.dataframe(stats_table, use_container_width=True, hide_index=True)
        with st.expander("TradingView CSV absorption events", expanded=False):
            st.dataframe(events_table.tail(300), use_container_width=True, hide_index=True)
    else:
        st.markdown(
            '<div class="tiny-status">TradingView CSV baseline: 未入力。Squeeze Confidenceは現在条件ベースのスコアです。</div>',
            unsafe_allow_html=True
        )

    # setup / trigger / tape-confirmed が多すぎる時の表示フィルター。
    # Support / Resistance / Liquidity thin は検証材料なので基本的に残す。
    squeeze_point_types = {
        "Short squeeze setup",
        "Short squeeze trigger",
        "Long squeeze setup",
        "Long squeeze trigger",
        "Tape-confirmed squeeze",
        "Upside spike risk",
        "Downside spike risk",
    }
    filtered_important_points = important_points.copy()
    try:
        if hide_low_confidence_points and len(filtered_important_points) > 0:
            is_squeeze = filtered_important_points["type"].isin(squeeze_point_types)
            is_liquidity_thin = filtered_important_points["type"].eq("Liquidity thin move")

            other_points = filtered_important_points[~is_squeeze & ~is_liquidity_thin].copy()

            # スクイーズ系は1種類に偏らないよう、typeごとに上位を残す。
            squeeze_points = filtered_important_points[is_squeeze].copy()
            keep_squeeze_frames = []
            if len(squeeze_points) > 0:
                squeeze_points["_conf_for_filter"] = pd.to_numeric(squeeze_points["squeeze_confidence"], errors="coerce").fillna(0)
                for point_type, sub in squeeze_points.groupby("type", sort=False):
                    keep_by_threshold = sub[sub["_conf_for_filter"] >= float(min_squeeze_confidence)].copy()
                    keep_by_rank = sub.sort_values(["_conf_for_filter", "score", "tape_score"], ascending=False).head(int(max_squeeze_icons))
                    keep_type = pd.concat([keep_by_threshold, keep_by_rank], ignore_index=False).drop_duplicates(subset=["point_id"])
                    keep_squeeze_frames.append(keep_type)
            keep_squeeze = pd.concat(keep_squeeze_frames, ignore_index=False) if keep_squeeze_frames else squeeze_points.iloc[0:0].copy()
            keep_squeeze = keep_squeeze.drop(columns=["_conf_for_filter"], errors="ignore")

            # Liquidity thin move は多くなりやすいので、スコア上位約1/3だけ残す。
            liquidity_points = filtered_important_points[is_liquidity_thin].copy()
            if len(liquidity_points) > 0:
                liquidity_points["_liq_rank_score"] = (
                    pd.to_numeric(liquidity_points.get("liquidity_thin_score", 0), errors="coerce").fillna(0) * 0.50 +
                    pd.to_numeric(liquidity_points.get("delta_impact_score", 0), errors="coerce").fillna(0) * 0.20 +
                    pd.to_numeric(liquidity_points.get("price_impact_per_BTC", 0), errors="coerce").fillna(0).clip(upper=100) * 0.20 +
                    pd.to_numeric(liquidity_points.get("score", 0), errors="coerce").fillna(0) * 0.10
                )
                keep_n = max(1, int(round(len(liquidity_points) * float(liquidity_keep_pct) / 100.0)))
                keep_liquidity = liquidity_points.sort_values("_liq_rank_score", ascending=False).head(keep_n)
                keep_liquidity = keep_liquidity.drop(columns=["_liq_rank_score"], errors="ignore")
            else:
                keep_liquidity = liquidity_points

            filtered_important_points = pd.concat([other_points, keep_squeeze, keep_liquidity], ignore_index=False)
            filtered_important_points = filtered_important_points.sort_values(["time_5m", "icon_side", "score"], ascending=[True, True, False]).copy()
    except Exception:
        pass

    if len(important_points) != len(filtered_important_points):
        hidden_count = len(important_points) - len(filtered_important_points)
        st.markdown(
            f'<div class="tiny-status">Icon filter: squeeze confidence >= {float(min_squeeze_confidence):.1f}% or top {int(max_squeeze_icons)} per type / liquidity thin top {float(liquidity_keep_pct):.0f}% / hidden {hidden_count}</div>',
            unsafe_allow_html=True
        )

    selected_point = None

    if len(filtered_important_points) > 0:
        valid_ids = filtered_important_points["point_id"].tolist()

        if "selected_point_id" not in st.session_state or st.session_state["selected_point_id"] not in valid_ids:
            st.session_state["selected_point_id"] = valid_ids[0]

        st.subheader("Important Points")

        display_points = filtered_important_points.copy().reset_index(drop=True)
        display_points["Focus"] = display_points["point_id"] == st.session_state["selected_point_id"]
        display_points["time"] = display_points["time_5m"].dt.strftime("%m/%d %H:%M")

        editor_columns = [
            "Focus", "No", "time", "type", "score", "reason",
            "support_or_resistance_status", "squeeze_confidence", "historical_probability_%", "tape_score",
            "absorption_high", "absorption_low", "break_level", "invalid_level",
            "price_impact_per_BTC", "liquidity_thin_score", "delta_impact_score",
            "same_side_streak", "large_trade_count", "memo",
            "open", "high", "low", "close",
            "volume_BTC", "delta_BTC",
            "buy_ratio_%", "sell_ratio_%"
        ]
        editor_columns = [c for c in editor_columns if c in display_points.columns]
        editor_df = display_points[editor_columns]

        edited_points = st.data_editor(
            editor_df,
            use_container_width=True,
            hide_index=True,
            disabled=[c for c in editor_df.columns if c != "Focus"],
            column_config={
                "Focus": st.column_config.CheckboxColumn(
                    "Focus",
                    help="Check one row to update Selected Point Details.",
                    default=False
                )
            },
            key=f"important_points_editor_{product_id}_{range_start.strftime('%Y%m%d%H%M%S')}_{range_end.strftime('%Y%m%d%H%M%S')}_{len(filtered_important_points)}"
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

        selected_point = filtered_important_points[
            filtered_important_points["point_id"] == st.session_state["selected_point_id"]
        ].iloc[0]

        auto_detail_types = {
            "Short squeeze setup",
            "Long squeeze setup",
            "Short squeeze trigger",
            "Long squeeze trigger",
            "Tape-confirmed squeeze",
            "Upside spike risk",
            "Downside spike risk",
        }
        if selected_point["type"] in auto_detail_types:
            auto_detail_time = selected_point["time_5m"].strftime("%Y-%m-%d %H:%M:%S")
            if st.session_state.get("detail_5m_start_str") != auto_detail_time:
                st.session_state["pending_detail_5m_start_str"] = auto_detail_time
                st.rerun()

    st.subheader("Coinbase 5m Chart")

    chart_points = filtered_important_points
    if len(filtered_important_points) > 0 and len(visible_icon_types) > 0:
        chart_points = filtered_important_points[filtered_important_points["type"].isin(visible_icon_types)].copy()
    elif len(visible_icon_types) == 0:
        chart_points = filtered_important_points.iloc[0:0].copy()

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
        sr_levels=sr_levels,
        legend_types=visible_icon_types
    )

    if selected_point is not None:
        hist_prob = selected_point.get("historical_probability_%", pd.NA)
        hist_prob_text = "N/A" if pd.isna(hist_prob) else f"{float(hist_prob):.1f}%"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Selected Point Details</div>
                <div class="metric-value">{selected_point['label']}</div>
                <div class="metric-label" style="margin-top:6px;">Squeeze Confidence</div>
                <div class="metric-value">{float(selected_point.get('squeeze_confidence', 0)):.1f}%</div>
                <div class="metric-label" style="margin-top:6px;">Historical Probability / TV CSV</div>
                <div class="metric-value">{hist_prob_text}</div>
                <div class="metric-label" style="margin-top:6px;">Reason</div>
                <div style="font-size:11px; line-height:1.45; color:#c8c3b8;">{selected_point['reason']}</div>
                <div class="metric-label" style="margin-top:6px;">Status / Memo</div>
                <div style="font-size:11px; line-height:1.45; color:#c8c3b8;">{selected_point.get('support_or_resistance_status', '')}<br>{selected_point.get('memo', '')}</div>
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
        tv_probability_stats = analyze_tradingview_probability(tv_csv_files, tv_lookahead_bars) if tv_csv_files else {
            "stats_table": pd.DataFrame(),
            "events_table": pd.DataFrame(),
            "lookup": {},
            "source_count": 0,
            "note": "TradingView CSV未入力"
        }

        important_points = detect_important_points(summary_5m, tv_probability_stats=tv_probability_stats)

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
            "requested_hours_back": int(hours_back),
            "max_history_hours": int(max_history_hours),
            "df_candles": df_candles,
            "df_range": df_range,
            "summary_5m": summary_5m,
            "important_points": important_points,
            "volume_by_price_all": volume_by_price_all,
            "side_price_volume_all": side_price_volume_all,
            "sr_levels": sr_levels,
            "tv_probability_stats": tv_probability_stats,
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
