"""
Cleaning, outlier removal and feature engineering for the raw M1 csv files, as a script so it can run
in the daily GitHub Actions job. Same logic as cell 11 of data_cleaning_and_exploration.ipynb
(the notebook keeps the plots and statistical tests for exploration).

Usage: python pipeline/transform.py <raw_dir> <processed_dir>
"""
import os
import sys

import numpy as np
import pandas as pd
from pyspark.sql import SparkSession, Window, functions, types

os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)


def time_window():
    # every time based operation (forward fill, lag, rolling windows) needs the rows in time order.
    # built on demand because pyspark needs an active session to create a window
    return Window.orderBy("Time")

schema = types.StructType([
    types.StructField("Time", types.TimestampType(), True),
    types.StructField("Open", types.DoubleType(), True),
    types.StructField("High", types.DoubleType(), True),
    types.StructField("Low", types.DoubleType(), True),
    types.StructField("Close", types.DoubleType(), True),
    types.StructField("Volume", types.DoubleType(), True)
])


def read_raw(spark, raw_dir):
    """Reads every tab separated csv in raw_dir into a dict of spark dataframes keyed by file name."""
    dfs = {}
    for file in sorted(os.listdir(raw_dir)):
        if file.endswith(".csv"):
            dfs[os.path.splitext(file)[0]] = spark.read.csv(os.path.join(raw_dir, file), header=True, schema=schema, sep="\t")
    return dfs


def cleaner(files: dict) -> dict:
    """Drops duplicate timestamps, forward fills NAs and removes inconsistent candles."""
    for name, file in files.items():
        print(f"Processing {name} for data cleaning...")
        file = file.filter(functions.col("Time").isNotNull()).dropDuplicates(["Time"])
        ffill_window = time_window().rowsBetween(Window.unboundedPreceding, 0)
        for col_name in ['Open', 'High', 'Low', 'Close', 'Volume']:
            file = file.withColumn(col_name, functions.last(col_name, ignorenulls=True).over(ffill_window))
        file = file.dropna()
        file = file.filter(
            (functions.col("Low") <= functions.col("High")) &
            functions.col("Open").between(functions.col("Low"), functions.col("High")) &
            functions.col("Close").between(functions.col("Low"), functions.col("High"))
        )
        files[name] = file
    return files


def extreme_value_remover(files: dict, k: float = 5.0) -> dict:
    """Removes single-candle spikes: the move into and out of the candle are both beyond the
    IQR fences of 1-minute log returns and in opposite directions."""
    cleaned_files = {}
    for name, df in files.items():
        print(f"Processing {name} for outlier removal...")
        minutes = functions.col("Time").cast("long") / 60
        returns_df = df \
            .withColumn("ret_in", functions.log("Close") - functions.log(functions.lag("Close").over(time_window()))) \
            .withColumn("ret_out", functions.lead("ret_in").over(time_window())) \
            .withColumn("gap_in", minutes - functions.lag(minutes).over(time_window())) \
            .withColumn("gap_out", functions.lead("gap_in").over(time_window()))

        q1, q3 = returns_df.selectExpr("percentile_approx(ret_in, array(0.25, 0.75), 10000) as percentiles").collect()[0][0]
        iqr = q3 - q1
        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr

        def is_extreme(c):
            return (functions.col(c) < lower_bound) | (functions.col(c) > upper_bound)

        is_spike = (
            is_extreme("ret_in") & is_extreme("ret_out") &
            (functions.signum("ret_in") != functions.signum("ret_out")) &
            (functions.col("gap_in") <= 1) & (functions.col("gap_out") <= 1)
        )
        filtered_df = returns_df \
            .filter(~functions.coalesce(is_spike, functions.lit(False))) \
            .drop("ret_in", "ret_out", "gap_in", "gap_out")

        row_count = df.count()
        new_rows = filtered_df.count()
        print(f"  {row_count} -> {new_rows} rows, removed {row_count - new_rows} ({(row_count - new_rows) / row_count * 100:.2f}%)")
        cleaned_files[name] = filtered_df
    return cleaned_files


def feature_engineering(clean_files: dict) -> dict:
    """Adds technical indicators, returns pandas dataframes sorted by time."""
    engineered_files = {}
    for name, file in clean_files.items():
        print(f"Feature engineering process for {name}")
        pandas_df = file.orderBy("Time").toPandas().reset_index(drop=True)

        pandas_df['MA5'] = pandas_df["Close"].rolling(window=5).mean()
        pandas_df['MA20'] = pandas_df["Close"].rolling(window=20).mean()

        pandas_df['MA20_std'] = pandas_df['Close'].rolling(window=20).std()
        pandas_df['BB_upper'] = pandas_df['MA20'] + (pandas_df['MA20_std'] * 2)
        pandas_df['BB_lower'] = pandas_df['MA20'] - (pandas_df['MA20_std'] * 2)

        pandas_df['Price_Change'] = pandas_df['Close'].diff()
        pandas_df['Price_Change_Pct'] = pandas_df['Close'].pct_change() * 100

        pandas_df['Daily_Range'] = pandas_df['High'] - pandas_df['Low']
        pandas_df['Daily_Range_Pct'] = ((pandas_df['High'] - pandas_df['Low']) / pandas_df['Low']) * 100

        tr1 = pandas_df['High'] - pandas_df['Low']
        tr2 = abs(pandas_df['High'] - pandas_df['Close'].shift(1))
        tr3 = abs(pandas_df['Low'] - pandas_df['Close'].shift(1))
        pandas_df['True_Range'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        pandas_df['ATR14'] = pandas_df['True_Range'].rolling(window=14).mean()

        delta = pandas_df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        pandas_df['RSI14'] = 100 - (100 / (1 + rs))
        pandas_df.loc[(avg_gain == 0) & (avg_loss == 0), 'RSI14'] = 50

        pandas_df['EMA12'] = pandas_df['Close'].ewm(span=12, adjust=False).mean()
        pandas_df['EMA26'] = pandas_df['Close'].ewm(span=26, adjust=False).mean()
        pandas_df['MACD'] = pandas_df['EMA12'] - pandas_df['EMA26']
        pandas_df['MACD_Signal'] = pandas_df['MACD'].ewm(span=9, adjust=False).mean()
        pandas_df['MACD_Hist'] = pandas_df['MACD'] - pandas_df['MACD_Signal']

        # warm-up rows of the rolling windows are dropped, not filled with values from the future
        pandas_df = pandas_df.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)
        engineered_files[name] = pandas_df
        print(f"  {len(pandas_df)} rows, {len(pandas_df.columns) - len(file.columns)} new features")
    return engineered_files


def main(raw_dir, processed_dir):
    spark = SparkSession.builder.appName("forex_transform").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    try:
        dfs = feature_engineering(extreme_value_remover(cleaner(read_raw(spark, raw_dir))))
    finally:
        spark.stop()
    os.makedirs(processed_dir, exist_ok=True)
    for name, df in dfs.items():
        path = os.path.join(processed_dir, f"{name}_processed.csv")
        df.to_csv(path, index=False)
        print(f"saved {path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
