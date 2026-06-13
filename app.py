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
    .stApp {
        background-color: #0f111a;
        color: #d1d4dc;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #0f111a 0%, #131722 100%);
    }

    [data-testid="stSidebar"] {
        background-color: #131722;
        border-right: 1px solid #2a2e39;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2.2rem;
    }

    .block-container {
        padding-top: 3.4rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    .tv-header {
        background-color: #131722;
        border: 1px solid #2a2e39;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.02);
    }

    .tv-title {
        font-size: 26px;
        font-weight: 800;
        color: #f0f3fa;
        letter-spacing: 0.3px;
    }

    .tv-subtitle {
        font-size: 13px;
        color: #9aa4b2;
        margin-top: 4px;
    }

    .tv-badge {
        background-color: #1e222d;
        border: 1px solid #2a2e39;
        border-radius: 999px;
        padding: 6px 12px;
        color: #22ab94;
        font-size: 13px;
        font-weight: 700;
        white-space: nowrap;
    }

    .metric-card {
        background-color: #131722;
        border: 1px solid #2a2e39;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    .metric-label {
        font-size: 12px;
        color: #9aa4b2;
        margin-bottom: 4px;
    }

    .metric-value {
        font-size: 22px;
        font-weight: 800;
        color: #f0f3fa;
    }

    .metric-green {
        color: #22ab94;
    }

    .metric-red {
        color: #f23645;
    }

    label {
        color: #b2b5be !important;
        font-weight: 700 !important;
    }

    input, textarea, select {
        background-color: #1e222d !important;
        color: #d1d4dc !important;
        border: 1px solid #2a2e39 !important;
        border-radius: 8px !important;
    }

    .stButton > button {
        background-color: #2962ff;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.65rem 1.2rem;
        font-weight: 800;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #1e53e5;
        color: white;
    }

    .stDownloadButton > button {
        background-color: #1e222d;
        color: #d1d4dc;
        border: 1px solid #2a2e39;
        border-radius: 8px;
        font-weight: 700;
    }

    .stDownloadButton > button:hover {
        background-color: #2a2e39;
        color: #ffffff;
    }

    [data-testid="stDataFrame"] {
        background-color: #131722;
        border: 1px solid #2a2e39;
        border-radius: 10px;
        overflow: hidden;
    }

    h1, h2, h3 {
        color: #f0f3fa !important;
    }

    .stAlert {
        background-color: #1e222d;
        border: 1px solid #2a2e39;
        border-radius: 8px;
        color: #d1d4dc;
    }

    [data-testid="stMetric"] {
        background-color: #131722;
        border: 1px solid #2a2e39;
        border-radius: 10px;
        padding: 12px;
    }

    hr {
        border-color: #2a2e39;
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
            <div class="tv-title">BTC CDV / Absorption Analyzer</div>
            <div class="tv-subtitle">
                Coinbase API × 5分足CDV × 吸収判定 × 防衛ライン確認
            </div>
        </div>
        <div class="tv-badge">LIVE API MODE</div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# サイドバー入力
# =========================================================

with st.sidebar:
    st.markdown("### Settings")

    product_id = st.text_input("Product ID", value="BTC-USD")

    hours_back = st.number_input(
        "何時間前から取得するか",
        min_value=1,
        max_value=24,
        value=6,
        step=1
    )

    detail_5m_start_str = st.text_input(
        "詳しく見る5分足 JST",
        value="2026-06-13 20:55:00"
    )

    price_round_digit = st.selectbox(
        "価格帯別出来高の丸め",
        options=[0, 1, 2],
        index=1,
        format_func=lambda x: {
            0: "1ドル刻み",
            1: "0.1ドル刻み",
            2: "0.01ドル刻み"
        }[x]
    )

    st.markdown("---")

    run = st.button("解析実行")


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
            # side=sell → 売り板が約定 → takerは買い成行っぽい
            # side=buy  → 買い板が約定 → takerは売り成行っぽい
            taker_side = "買い成行っぽい" if side == "sell" else "売り成行っぽい"

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
            increasing_line_color="#22ab94",
            decreasing_line_color="#f23645",
            increasing_fillcolor="#22ab94",
            decreasing_fillcolor="#f23645",
            name=product_id
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=df_candles["time"],
            y=df_candles["volume"],
            marker_color="#363a45",
            name="Volume"
        ),
        row=2,
        col=1
    )

    # 重要ポイントをチャートにマーカー表示
    if important_points is not None and len(important_points) > 0:
        marker_colors = {
            "買い吸収": "#22ab94",
            "買い確認": "#2962ff",
            "売り吸収": "#f23645",
            "売り確認": "#ff9800",
            "ショートスクイーズ候補": "#00e676",
            "ロングスクイーズ候補": "#ff5252",
            "高出来高": "#b2b5be"
        }

        marker_symbols = {
            "買い吸収": "triangle-up",
            "買い確認": "circle",
            "売り吸収": "triangle-down",
            "売り確認": "x",
            "ショートスクイーズ候補": "star",
            "ロングスクイーズ候補": "star",
            "高出来高": "diamond"
        }

        for point_type, group in important_points.groupby("type"):
            fig.add_trace(
                go.Scatter(
                    x=group["time_5m"],
                    y=group["spot_price"],
                    mode="markers",
                    marker=dict(
                        size=12,
                        color=marker_colors.get(point_type, "#ffffff"),
                        symbol=marker_symbols.get(point_type, "circle"),
                        line=dict(width=1, color="#ffffff")
                    ),
                    name=point_type,
                    text=group["reason"],
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        "time=%{x}<br>"
                        "price=%{y}<extra></extra>"
                    )
                ),
                row=1,
                col=1
            )

    # POC / サポート / レジスタンス候補の水平線
    if sr_levels is not None and len(sr_levels) > 0:
        for _, level in sr_levels.iterrows():
            kind = level["kind"]
            price = float(level["price"])
            volume = float(level["volume_BTC"])

            if kind == "POC":
                color = "#ffd54f"
                dash = "solid"
            elif kind == "Support":
                color = "#22ab94"
                dash = "dot"
            else:
                color = "#f23645"
                dash = "dot"

            fig.add_hline(
                y=price,
                line_color=color,
                line_dash=dash,
                line_width=2,
                annotation_text=f"{kind} {price:.1f} / {volume:.2f} BTC",
                annotation_position="right",
                row=1,
                col=1
            )

    # 選択したポイントをスポット表示
    if selected_point is not None:
        selected_time = selected_point["time_5m"]
        selected_end = selected_time + pd.Timedelta(minutes=5)
        selected_price = selected_point["spot_price"]
        selected_label = selected_point["label"]

        fig.add_vrect(
            x0=selected_time,
            x1=selected_end,
            fillcolor="#2962ff",
            opacity=0.18,
            line_width=0,
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=[selected_time],
                y=[selected_price],
                mode="markers+text",
                marker=dict(
                    size=22,
                    color="#ffd54f",
                    symbol="circle-open",
                    line=dict(width=3, color="#ffd54f")
                ),
                text=["SPOT"],
                textposition="top center",
                name="Selected Spot",
                hovertemplate=f"<b>{selected_label}</b><extra></extra>"
            ),
            row=1,
            col=1
        )

        fig.add_annotation(
            x=selected_time,
            y=selected_price,
            text=selected_label,
            showarrow=True,
            arrowhead=2,
            ax=40,
            ay=-60,
            bgcolor="#1e222d",
            bordercolor="#ffd54f",
            font=dict(color="#f0f3fa", size=11),
            row=1,
            col=1
        )

    fig.update_layout(
        height=720,
        xaxis_rangeslider_visible=False,
        title=f"Coinbase {product_id} 5分足チャート",
        template="plotly_dark",
        paper_bgcolor="#131722",
        plot_bgcolor="#131722",
        font=dict(color="#d1d4dc"),
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(
        gridcolor="#2a2e39",
        zerolinecolor="#2a2e39",
        rangeslider_visible=False
    )

    fig.update_yaxes(
        gridcolor="#2a2e39",
        zerolinecolor="#2a2e39"
    )

    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# 5分足CDV集計
# =========================================================

def make_5m_summary(df_range):
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
        df_range[df_range["taker_side_estimate"] == "買い成行っぽい"]
        .groupby("time_5m")["size_BTC"]
        .sum()
    )

    sell_5m = (
        df_range[df_range["taker_side_estimate"] == "売り成行っぽい"]
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

    # 売り成行が多いのに陽線 or 下がらない = 買い吸収候補
    summary_5m["buy_absorption_candidate"] = (
        (summary_5m["sell_ratio_%"] >= 60) &
        (summary_5m["candle_move"] >= 0)
    )

    # 買い成行が多い陽線 = 買い確認足
    summary_5m["bullish_confirmation"] = (
        (summary_5m["buy_ratio_%"] >= 65) &
        (summary_5m["candle_move"] > 0)
    )

    # 買い成行が多いのに陰線 or 上がらない = 売り吸収候補
    summary_5m["sell_absorption_candidate"] = (
        (summary_5m["buy_ratio_%"] >= 60) &
        (summary_5m["candle_move"] <= 0)
    )

    # 売り成行が多い陰線 = 売り確認足
    summary_5m["bearish_confirmation"] = (
        (summary_5m["sell_ratio_%"] >= 65) &
        (summary_5m["candle_move"] < 0)
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
# POC / サポート / レジスタンス候補
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
            "memo": "現在値より下の出来高集中帯。サポート候補。"
        })

    for _, r in resistances.iterrows():
        levels.append({
            "kind": "Resistance",
            "price": float(r["price_bin"]),
            "volume_BTC": float(r["size_BTC"]),
            "distance_from_current": float(r["price_bin"] - current_price),
            "memo": "現在値より上の出来高集中帯。レジスタンス候補。"
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
            "buy_ratio_%": row["buy_ratio_%"],
            "sell_ratio_%": row["sell_ratio_%"],
            "candle_move": row["candle_move"],
        }

        if row["buy_absorption_candidate"]:
            score = 80 + min(15, max(0, row["sell_ratio_%"] - 60) / 2)
            rows.append({
                **base,
                "type": "買い吸収",
                "score": round(score, 1),
                "reason": f"売り成行{row['sell_ratio_%']:.1f}%なのにローソクが下がらない/陽線。買い吸収候補。"
            })

        if row["bullish_confirmation"]:
            score = 70 + min(20, max(0, row["buy_ratio_%"] - 65) / 2)
            rows.append({
                **base,
                "type": "買い確認",
                "score": round(score, 1),
                "reason": f"買い成行{row['buy_ratio_%']:.1f}%で陽線。上方向の確認足候補。"
            })

        if row["sell_absorption_candidate"]:
            score = 80 + min(15, max(0, row["buy_ratio_%"] - 60) / 2)
            rows.append({
                **base,
                "type": "売り吸収",
                "score": round(score, 1),
                "reason": f"買い成行{row['buy_ratio_%']:.1f}%なのに上がらない/陰線。売り吸収候補。"
            })

        if row["bearish_confirmation"]:
            score = 70 + min(20, max(0, row["sell_ratio_%"] - 65) / 2)
            rows.append({
                **base,
                "type": "売り確認",
                "score": round(score, 1),
                "reason": f"売り成行{row['sell_ratio_%']:.1f}%で陰線。下方向の確認足候補。"
            })

        if row["volume_BTC"] >= vol_threshold:
            rows.append({
                **base,
                "type": "高出来高",
                "score": 60,
                "reason": f"選択期間内で上位20%の出来高。出来高集中ポイント。"
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
                "type": "ショートスクイーズ候補",
                "score": 95,
                "reason": f"{row['time_5m']}の買い吸収後、{confirm['time_5m']}で買い確認。ショートスクイーズ候補。"
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
                "type": "ロングスクイーズ候補",
                "score": 95,
                "reason": f"{row['time_5m']}の売り吸収後、{confirm['time_5m']}で売り確認。ロングスクイーズ候補。"
            })

    if not rows:
        return pd.DataFrame()

    points = pd.DataFrame(rows)
    points = points.drop_duplicates(subset=["time_5m", "type"])
    points = points.sort_values(["score", "volume_BTC"], ascending=False).reset_index(drop=True)

    points["label"] = points.apply(
        lambda r: f"{r['time_5m'].strftime('%m/%d %H:%M')}｜{r['type']}｜score {r['score']}｜close {r['close']:.2f}",
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
        df_detail["taker_side_estimate"] == "買い成行っぽい"
    ]["size_BTC"].sum()

    sell_qty = df_detail[
        df_detail["taker_side_estimate"] == "売り成行っぽい"
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
# 実行
# =========================================================

if run:
    tz = "Asia/Tokyo"

    range_end = pd.Timestamp.now(tz=tz)
    range_start = range_end - pd.Timedelta(hours=int(hours_back))

    st.info(f"取得範囲: {range_start} 〜 {range_end}")

    # -----------------------------------------------------
    # ローソク足取得
    # -----------------------------------------------------

    df_candles = fetch_coinbase_candles(
        product_id=product_id,
        range_start=range_start,
        range_end=range_end,
        granularity=300
    )

    # -----------------------------------------------------
    # 約定履歴取得
    # -----------------------------------------------------

    df_range = fetch_coinbase_trades(
        product_id=product_id,
        range_start=range_start,
        range_end=range_end,
        tz=tz
    )

    if len(df_range) == 0:
        st.error("約定データが取得できませんでした。")
        st.stop()

    st.success(f"約定履歴取得完了: {len(df_range)} 件")

    # -----------------------------------------------------
    # 5分足CDV集計・重要ポイント抽出
    # -----------------------------------------------------

    summary_5m = make_5m_summary(df_range)
    important_points = detect_important_points(summary_5m)

    latest = summary_5m.tail(1).iloc[0]
    current_price = float(latest["close"])

    volume_by_price_all, side_price_volume_all, sr_levels = calculate_volume_profile_levels(
        df_range=df_range,
        current_price=current_price,
        price_round_digit=price_round_digit,
        top_n=3
    )

    selected_point = None

    if len(important_points) > 0:
        st.subheader("重要ポイントピックアップ")
        selected_label = st.radio(
            "クリックするとチャート上で該当ローソクをスポット表示します",
            important_points["label"].tolist(),
            index=0,
            horizontal=False
        )
        selected_point = important_points[important_points["label"] == selected_label].iloc[0]

    st.subheader("Coinbase 5分足チャート")
    show_candlestick_chart(
        df_candles,
        product_id,
        important_points=important_points,
        selected_point=selected_point,
        sr_levels=sr_levels
    )

    if len(important_points) > 0:
        st.subheader("重要ポイント一覧")
        st.dataframe(
            important_points[[
                "time_5m", "type", "score", "reason",
                "open", "high", "low", "close",
                "volume_BTC", "delta_BTC",
                "buy_ratio_%", "sell_ratio_%"
            ]],
            use_container_width=True
        )

    latest = summary_5m.tail(1).iloc[0]

    if len(sr_levels) > 0:
        st.subheader("POC / サポート / レジスタンス候補")
        st.dataframe(sr_levels, use_container_width=True)

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

    st.subheader("5分足CDV集計 最新30本")
    st.dataframe(summary_5m.tail(30), use_container_width=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "買い吸収候補",
        "買い確認足",
        "売り吸収候補",
        "売り確認足",
        "防衛ライン候補"
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
    # 全体価格帯別出来高
    # -----------------------------------------------------

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("全体 価格帯別出来高 TOP30")
        st.dataframe(volume_by_price_all.head(30), use_container_width=True)

    with col_b:
        st.subheader("全体 価格帯別 × 成行方向 TOP30")
        st.dataframe(side_price_volume_all.head(30), use_container_width=True)

    # -----------------------------------------------------
    # CSVダウンロード
    # -----------------------------------------------------

    st.subheader("CSVダウンロード")

    dl1, dl2, dl3, dl4 = st.columns(4)

    with dl1:
        st.download_button(
            "約定履歴CSV",
            df_range.to_csv(index=False).encode("utf-8-sig"),
            file_name="trades.csv",
            mime="text/csv"
        )

    with dl2:
        st.download_button(
            "5分足CDV CSV",
            summary_5m.to_csv().encode("utf-8-sig"),
            file_name="5m_cdv_summary.csv",
            mime="text/csv"
        )

    with dl3:
        st.download_button(
            "価格帯別出来高CSV",
            volume_by_price_all.to_csv(index=False).encode("utf-8-sig"),
            file_name="volume_by_price_all.csv",
            mime="text/csv"
        )

    with dl4:
        st.download_button(
            "価格帯×成行CSV",
            side_price_volume_all.to_csv().encode("utf-8-sig"),
            file_name="side_price_volume_all.csv",
            mime="text/csv"
        )

    # -----------------------------------------------------
    # 特定5分足 詳細解析
    # -----------------------------------------------------

    if detail_5m_start_str.strip():
        try:
            detail_start = pd.Timestamp(detail_5m_start_str, tz=tz)
        except Exception:
            st.error("詳しく見る5分足の日時形式が不正です。例: 2026-06-13 20:55:00")
            st.stop()

        detail = analyze_detail_5m(
            df_range=df_range,
            detail_start=detail_start,
            price_round_digit=price_round_digit
        )

        st.subheader("特定5分足 詳細解析")

        if detail is None:
            st.warning("指定した5分足のデータがありません。取得時間範囲内か確認してください。")
        else:
            st.write("詳細サマリー")
            st.dataframe(detail["detail_summary"], use_container_width=True)

            detail_tab1, detail_tab2, detail_tab3, detail_tab4, detail_tab5, detail_tab6 = st.tabs([
                "価格帯別出来高",
                "価格帯×成行方向",
                "秒ごとの出来高",
                "同時刻複数約定",
                "同じサイズ連打",
                "連続買い/売り"
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

            st.subheader("特定5分足 CSVダウンロード")

            d1, d2, d3, d4 = st.columns(4)

            with d1:
                st.download_button(
                    "詳細約定CSV",
                    detail["df_detail"].to_csv(index=False).encode("utf-8-sig"),
                    file_name="detail_trades.csv",
                    mime="text/csv"
                )

            with d2:
                st.download_button(
                    "詳細サマリーCSV",
                    detail["detail_summary"].to_csv(index=False).encode("utf-8-sig"),
                    file_name="detail_summary.csv",
                    mime="text/csv"
                )

            with d3:
                st.download_button(
                    "詳細価格帯CSV",
                    detail["volume_by_price"].to_csv(index=False).encode("utf-8-sig"),
                    file_name="detail_volume_by_price.csv",
                    mime="text/csv"
                )

            with d4:
                st.download_button(
                    "詳細秒別CSV",
                    detail["volume_by_second"].to_csv().encode("utf-8-sig"),
                    file_name="detail_volume_by_second.csv",
                    mime="text/csv"
                )
else:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Ready</div>
            <div class="metric-value">左の設定を確認して「解析実行」を押してください</div>
        </div>
        """,
        unsafe_allow_html=True
    )
