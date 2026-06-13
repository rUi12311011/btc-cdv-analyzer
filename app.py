import streamlit as st
import requests
import pandas as pd
import time
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="BTC CDV Analyzer",
    layout="wide"
)

st.title("BTC CDV / Absorption Analyzer")

st.write("Coinbaseの約定履歴から、5分足CDV・買い比率・売り比率・吸収候補を確認するWebアプリです。")

# =========================
# 入力欄
# =========================

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

run = st.button("解析実行")

# =========================
# 関数
# =========================

def fetch_coinbase_trades(product_id, range_start, range_end, tz="Asia/Tokyo", max_pages=1000, sleep_sec=0.15):
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
            st.error(f"APIエラー: {res.status_code}")
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

        status.write(f"取得中 page {page + 1} / 最新 {newest} / 最古 {oldest} / 件数 {len(df_temp)}")
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

    summary_5m["delta_BTC"] = summary_5m["buy_taker_BTC"] - summary_5m["sell_taker_BTC"]

    summary_5m["buy_ratio_%"] = summary_5m["buy_taker_BTC"] / summary_5m["volume_BTC"] * 100
    summary_5m["sell_ratio_%"] = summary_5m["sell_taker_BTC"] / summary_5m["volume_BTC"] * 100

    summary_5m["candle_move"] = summary_5m["close"] - summary_5m["open"]
    summary_5m["range"] = summary_5m["high"] - summary_5m["low"]

    summary_5m["buy_absorption_candidate"] = (
        (summary_5m["sell_ratio_%"] >= 60) &
        (summary_5m["candle_move"] >= 0)
    )

    summary_5m["bullish_confirmation"] = (
        (summary_5m["buy_ratio_%"] >= 65) &
        (summary_5m["candle_move"] > 0)
    )

    summary_5m["sell_absorption_candidate"] = (
        (summary_5m["buy_ratio_%"] >= 60) &
        (summary_5m["candle_move"] <= 0)
    )

    summary_5m["bearish_confirmation"] = (
        (summary_5m["sell_ratio_%"] >= 65) &
        (summary_5m["candle_move"] < 0)
    )

    summary_5m["lower_wick"] = summary_5m[["open", "close"]].min(axis=1) - summary_5m["low"]

    vol_median = summary_5m["volume_BTC"].median()

    summary_5m["defense_score"] = 0
    summary_5m.loc[summary_5m["buy_absorption_candidate"], "defense_score"] += 2
    summary_5m.loc[summary_5m["volume_BTC"] >= vol_median, "defense_score"] += 1
    summary_5m.loc[summary_5m["lower_wick"] > 0, "defense_score"] += 1
    summary_5m.loc[summary_5m["candle_move"] > 0, "defense_score"] += 1

    return summary_5m


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
    buy_qty = df_detail[df_detail["taker_side_estimate"] == "買い成行っぽい"]["size_BTC"].sum()
    sell_qty = df_detail[df_detail["taker_side_estimate"] == "売り成行っぽい"]["size_BTC"].sum()

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

    return {
        "df_detail": df_detail,
        "detail_summary": detail_summary,
        "volume_by_price": volume_by_price,
        "side_price_volume": side_price_volume,
        "volume_by_second": volume_by_second,
        "same_time": same_time
    }


# =========================
# 実行
# =========================

if run:
    tz = "Asia/Tokyo"

    range_end = pd.Timestamp.now(tz=tz)
    range_start = range_end - pd.Timedelta(hours=int(hours_back))

    st.info(f"取得範囲: {range_start} 〜 {range_end}")

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

    summary_5m = make_5m_summary(df_range)

    st.subheader("5分足CDV集計 最新30本")
    st.dataframe(summary_5m.tail(30), use_container_width=True)

    st.subheader("買い吸収候補")
    st.dataframe(
        summary_5m[summary_5m["buy_absorption_candidate"]],
        use_container_width=True
    )

    st.subheader("買い確認足")
    st.dataframe(
        summary_5m[summary_5m["bullish_confirmation"]],
        use_container_width=True
    )

    st.subheader("売り吸収候補")
    st.dataframe(
        summary_5m[summary_5m["sell_absorption_candidate"]],
        use_container_width=True
    )

    st.subheader("防衛ライン候補")
    defense_candidates = summary_5m[summary_5m["defense_score"] >= 3].sort_values(
        ["defense_score", "volume_BTC"],
        ascending=False
    )
    st.dataframe(defense_candidates, use_container_width=True)

    st.download_button(
        "約定履歴CSVをダウンロード",
        df_range.to_csv(index=False).encode("utf-8-sig"),
        file_name="trades.csv",
        mime="text/csv"
    )

    st.download_button(
        "5分足CDV集計CSVをダウンロード",
        summary_5m.to_csv().encode("utf-8-sig"),
        file_name="5m_cdv_summary.csv",
        mime="text/csv"
    )

    if detail_5m_start_str.strip():
        detail_start = pd.Timestamp(detail_5m_start_str, tz=tz)

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

            st.write("価格帯別出来高 TOP30")
            st.dataframe(detail["volume_by_price"].head(30), use_container_width=True)

            st.write("価格帯別 × 成行方向 TOP30")
            st.dataframe(detail["side_price_volume"].head(30), use_container_width=True)

            st.write("秒ごとの出来高 TOP30")
            st.dataframe(detail["volume_by_second"].head(30), use_container_width=True)

            st.write("同時刻複数約定 TOP30")
            st.dataframe(detail["same_time"].head(30), use_container_width=True)

            st.download_button(
                "特定5分足 約定履歴CSVをダウンロード",
                detail["df_detail"].to_csv(index=False).encode("utf-8-sig"),
                file_name="detail_trades.csv",
                mime="text/csv"
            )
