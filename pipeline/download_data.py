"""
Downloads 1-minute forex candles from Twelve Data and writes them in the same tab separated format as the
original raw files (Time, Open, High, Low, Close, Volume) so transform.py can read them unchanged.

Twelve Data returns no volume for forex, so Volume is written as 0 (the models only use Close).
The free plan allows 8 requests per minute and 800 per day; a 100 day download for 4 pairs is ~140 requests.

Usage: TWELVE_DATA_API_KEY=... python pipeline/download_data.py <raw_dir> [--days 100] [--pairs EURUSD GBPUSD]
"""
import argparse
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

API_URL = "https://api.twelvedata.com/time_series"
PAIRS = ["EURUSD", "GBPUSD", "USDCAD", "USDCHF"]
# one request returns at most 5000 bars, 3 days of minutes is 4320
CHUNK = timedelta(days=3)
# stay under 8 requests per minute
REQUEST_GAP_SECONDS = 8


def fetch_chunk(symbol, start, end, api_key):
    """Returns the candles between start and end as a dataframe, empty when the market was closed."""
    params = {
        "symbol": symbol,
        "interval": "1min",
        "start_date": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "end_date": end.strftime("%Y-%m-%dT%H:%M:%S"),
        "timezone": "UTC",
        "order": "asc",
        "outputsize": 5000,
        "apikey": api_key,
    }
    for attempt in range(4):
        body = requests.get(API_URL, params=params, timeout=60).json()
        if body.get("status") == "ok":
            return pd.DataFrame(body.get("values", []))
        code = body.get("code")
        message = body.get("message", "")
        if code == 429:
            # per-minute limit reached, wait for the next minute window
            print(f"  rate limited, waiting 65s ({message})")
            time.sleep(65)
            continue
        if "no data" in message.lower():
            # weekends and holidays
            return pd.DataFrame()
        raise RuntimeError(f"Twelve Data error for {symbol} {params['start_date']}: {code} {message}")
    raise RuntimeError(f"Twelve Data kept rate limiting {symbol} {params['start_date']}")


def download_pair(pair, days, api_key):
    symbol = f"{pair[:3]}/{pair[3:]}"
    end = datetime.now(timezone.utc).replace(second=0, microsecond=0, tzinfo=None)
    start = end - timedelta(days=days)
    chunks = []
    chunk_start = start
    while chunk_start < end:
        chunk_end = min(chunk_start + CHUNK, end)
        chunks.append(fetch_chunk(symbol, chunk_start, chunk_end, api_key))
        chunk_start = chunk_end
        time.sleep(REQUEST_GAP_SECONDS)

    df = pd.concat(chunks, ignore_index=True)
    if df.empty:
        raise RuntimeError(f"No data returned for {pair}")
    df = df.rename(columns={"datetime": "Time", "open": "Open", "high": "High", "low": "Low", "close": "Close"})
    df["Time"] = pd.to_datetime(df["Time"])
    for col in ["Open", "High", "Low", "Close"]:
        df[col] = df[col].astype(float)
    df["Volume"] = 0
    # chunk boundaries overlap by one minute
    df = df.drop_duplicates("Time").sort_values("Time")
    # Twelve Data also returns thin weekend quotes. The forex week runs from Sunday 17:00 to Friday 17:00
    # New York time (same as the original data), so everything outside that is dropped. Using New York time handles DST.
    ny = df["Time"].dt.tz_localize("UTC").dt.tz_convert("America/New_York")
    closed = ((ny.dt.dayofweek == 4) & (ny.dt.hour >= 17)) | (ny.dt.dayofweek == 5) | ((ny.dt.dayofweek == 6) & (ny.dt.hour < 17))
    df = df[~closed.values]
    return df[["Time", "Open", "High", "Low", "Close", "Volume"]]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_dir")
    parser.add_argument("--days", type=int, default=100)
    parser.add_argument("--pairs", nargs="+", default=PAIRS)
    args = parser.parse_args()

    api_key = os.environ.get("TWELVE_DATA_API_KEY")
    if not api_key:
        sys.exit("TWELVE_DATA_API_KEY is not set")

    os.makedirs(args.raw_dir, exist_ok=True)
    for pair in args.pairs:
        print(f"Downloading {pair} for the last {args.days} days...")
        df = download_pair(pair, args.days, api_key)
        path = os.path.join(args.raw_dir, f"{pair}_M1.csv")
        df.to_csv(path, sep="\t", index=False, date_format="%Y-%m-%d %H:%M:%S")
        print(f"  saved {len(df)} candles from {df.Time.iloc[0]} to {df.Time.iloc[-1]} to {path}")


if __name__ == "__main__":
    main()
