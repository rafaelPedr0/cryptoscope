

import requests
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path

BASE_URL = "https://api.coingecko.com/api/v3"
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def extract_top_cryptos(top_n: int = 50) -> list:
    endpoint = f"{BASE_URL}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": top_n,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "1h,24h,7d"
    }
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        raw_path = RAW_DIR / f"markets_{timestamp}.json"
        with open(raw_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[EXTRACT] ✅ {len(data)} criptos extraídas → {raw_path}")
        return data
    except requests.RequestException as e:
        print(f"[EXTRACT] ❌ Erro na API: {e}")
        return []


def extract_historical_prices(coin_id: str = "bitcoin", days: int = 90) -> dict:
    endpoint = f"{BASE_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    response = requests.get(endpoint, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def transform_market_data(raw_data: list) -> pd.DataFrame:
    if not raw_data:
        return pd.DataFrame()

    columns_map = {
        "id": "coin_id",
        "symbol": "symbol",
        "name": "name",
        "current_price": "price_usd",
        "market_cap": "market_cap",
        "total_volume": "volume_24h",
        "price_change_percentage_1h_in_currency": "change_1h_pct",
        "price_change_percentage_24h_in_currency": "change_24h_pct",
        "price_change_percentage_7d_in_currency": "change_7d_pct",
        "ath": "all_time_high",
        "ath_change_percentage": "ath_distance_pct",
    }

    df = pd.DataFrame(raw_data)[list(columns_map.keys())].rename(columns=columns_map)

    def classify_momentum(row):
        if row["change_24h_pct"] > 5:
            return "🚀 Alta Forte"
        elif row["change_24h_pct"] > 1:
            return "📈 Alta"
        elif row["change_24h_pct"] < -5:
            return "📉 Queda Forte"
        elif row["change_24h_pct"] < -1:
            return "🔻 Queda"
        else:
            return "➡️ Lateral"

    df["momentum"] = df.apply(classify_momentum, axis=1)
    df["volume_to_mktcap_ratio"] = (df["volume_24h"] / df["market_cap"]).round(4)
    df["recovery_stage"] = pd.cut(
        df["ath_distance_pct"],
        bins=[-100, -75, -50, -25, -10, 0],
        labels=["Fundo Profundo", "Recuperação", "Metade", "Próximo do ATH", "ATH Region"]
    )
    df["extracted_at"] = datetime.now().isoformat()
    df = df.sort_values("market_cap", ascending=False).reset_index(drop=True)
    print(f"[TRANSFORM] ✅ DataFrame: {df.shape[0]} linhas × {df.shape[1]} colunas")
    return df


def transform_historical(raw_hist: dict, coin_id: str) -> pd.DataFrame:
    prices = raw_hist.get("prices", [])
    volumes = raw_hist.get("total_volumes", [])
    df_price = pd.DataFrame(prices, columns=["timestamp_ms", "price"])
    df_vol = pd.DataFrame(volumes, columns=["timestamp_ms", "volume"])
    df = df_price.merge(df_vol, on="timestamp_ms")
    df["date"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
    df["coin"] = coin_id
    df["ma_7d"] = df["price"].rolling(7).mean()
    df["ma_30d"] = df["price"].rolling(30).mean()
    df["volatility_7d"] = df["price"].rolling(7).std()
    return df.drop(columns=["timestamp_ms"])


def load_to_csv(df: pd.DataFrame, filename: str) -> str:
    output_path = PROCESSED_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"[LOAD] ✅ Salvo em: {output_path}")
    return str(output_path)


def run_pipeline():
    print("\n" + "="*50)
    print("🚀 CryptoScope ETL Pipeline - Iniciando...")
    print("="*50)

    raw = extract_top_cryptos(top_n=50)
    df_market = transform_market_data(raw)

    if not df_market.empty:
        load_to_csv(df_market, "market_snapshot.csv")

    top5 = df_market["coin_id"].head(5).tolist()
    all_hist = []
    for coin in top5:
        try:
            raw_hist = extract_historical_prices(coin, days=90)
            df_hist = transform_historical(raw_hist, coin)
            all_hist.append(df_hist)
            print(f"[EXTRACT] ✅ Histórico: {coin}")
        except Exception as e:
            print(f"[WARN] Pulando {coin}: {e}")

    if all_hist:
        df_all_hist = pd.concat(all_hist, ignore_index=True)
        load_to_csv(df_all_hist, "price_history.csv")

    print("\n✅ Pipeline concluído com sucesso!")
    return df_market


if __name__ == "__main__":
    run_pipeline()