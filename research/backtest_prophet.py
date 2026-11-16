"""
Walk-forward backtest of the Prophet setups tried for this project, against a naive "price stays the same" forecast.

Protocol: for each pair and each cutoff (the last 4 Mondays of the data in processed/), train on everything before
the cutoff, forecast the next 5 days and score on hourly actual points. Regressors are unknown in the future, so
they are held at their last known value. "anchored" shifts a forecast so it starts at the last real close (same
effect as anchor_to_last_close in backend/model.py).

Usage: python research/backtest_prophet.py [processed_dir] [output_csv]
Takes ~10-15 minutes (the minute-level fits are the slow part), pairs run in parallel.
"""
import logging
import os
import sys
import warnings
from multiprocessing import Pool

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "processed")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "research", "backtest_summary.csv")
CUTOFFS = pd.to_datetime(["2025-02-24", "2025-03-03", "2025-03-10", "2025-03-17"])
HORIZON = pd.Timedelta(days=5)

# name: data frequency, regressors, Prophet settings
VARIANTS = {
    "minute, weekly, cps 0.01 (previous production)": ("min", [], dict(changepoint_prior_scale=0.01, weekly_seasonality=True)),
    "minute + ATR14/RSI14/MACD regressors": ("min", ["ATR14", "RSI14", "MACD"], dict(changepoint_prior_scale=0.01, weekly_seasonality=True)),
    "minute + MA20/Bollinger band regressors": ("min", ["MA20", "BB_upper", "BB_lower"], dict(changepoint_prior_scale=0.01, weekly_seasonality=True)),
    "hourly, weekly, cps 0.01": ("hour", [], dict(changepoint_prior_scale=0.01, weekly_seasonality=True)),
    "hourly, weekly, cps 0.1, changepoint_range 0.95": ("hour", [], dict(changepoint_prior_scale=0.1, changepoint_range=0.95, weekly_seasonality=True)),
    "hourly, no weekly, cps 0.01 (current production)": ("hour", [], dict(changepoint_prior_scale=0.01, weekly_seasonality=False)),
}


def to_hourly(df):
    return df.set_index("ds")[["y"]].resample("h").last().dropna().reset_index()


def run_pair(pair_file):
    logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
    from prophet import Prophet

    pair = pair_file.split("_")[0]
    df = pd.read_csv(os.path.join(DATA, pair_file))
    df["ds"] = pd.to_datetime(df["Time"])
    df["y"] = df["Close"]
    rows = []
    for cutoff in CUTOFFS:
        train_min = df[df.ds < cutoff]
        test = df[(df.ds >= cutoff) & (df.ds < cutoff + HORIZON)]
        test = test[test.ds.dt.minute == 0]
        last = train_min.iloc[-1]
        preds = {"naive: last close": np.full(len(test), last.y)}
        for name, (freq, regs, settings) in VARIANTS.items():
            train = to_hourly(train_min) if freq == "hour" else train_min[["ds", "y"] + regs]
            m = Prophet(daily_seasonality=False, **settings)
            for r in regs:
                m.add_regressor(r)
            m.fit(train)
            future = pd.concat([pd.DataFrame({"ds": [last.ds]}), test[["ds"]]], ignore_index=True)
            for r in regs:
                future[r] = last[r]
            fc = m.predict(future)["yhat"].values
            preds[name] = fc[1:]
            if not regs:
                preds[name + ", anchored"] = fc[1:] - fc[0] + last.y
        for name, p in preds.items():
            err = p - test.y.values
            for ds, e, actual in zip(test.ds, err, test.y.values):
                rows.append({"pair": pair, "cutoff": cutoff, "model": name,
                             "h_days": (ds - cutoff) / pd.Timedelta(days=1), "ape": abs(e) / actual * 100})
        print(f"{pair} {cutoff.date()} done", flush=True)
    return pd.DataFrame(rows)


def summarize(res):
    res = res[res.h_days > 0].copy()
    res["bucket"] = pd.cut(res.h_days, [0, 1, 3, 5], labels=["MAPE day 1", "MAPE days 2-3", "MAPE days 4-5"]).astype(str)
    weekly = res.groupby(["model", "pair", "cutoff"]).ape.mean().unstack("model")
    summary = res.groupby("model").ape.mean().rename("MAPE %").to_frame()
    summary = summary.join(res.pivot_table(index="model", columns="bucket", values="ape", aggfunc="mean"))
    summary["weeks beating naive (of 16)"] = [int((weekly[m] < weekly["naive: last close"]).sum()) for m in summary.index]
    return summary.sort_values("MAPE %").round(3)


if __name__ == "__main__":
    files = sorted(f for f in os.listdir(DATA) if f.endswith(".csv"))
    with Pool(len(files)) as pool:
        results = pd.concat(pool.map(run_pair, files))
    summary = summarize(results)
    summary.to_csv(OUT)
    print(summary.to_string())
    print("saved", OUT)
