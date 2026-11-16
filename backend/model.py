from prophet import Prophet
import pandas as pd
import sys
import os
import joblib


def anchor_to_last_close(model, history):
    """
    Shifts the fitted trend so the forecast starts at the last real close instead of Prophet's own
    fitted level, which can be ~1% off. The shift is applied to the trend offset parameter `m`, so every
    predict() call (and its uncertainty band) is anchored without any change in the serving code.
    """
    last = history.iloc[[-1]][["ds"]]
    offset = history["y"].iloc[-1] - model.predict(last)["yhat"].iloc[0]
    model.params["m"] = model.params["m"] + offset / model.y_scale
    model.anchor_offset = offset
    return offset


def create_and_save_models(data_dir, models_dir):

    os.makedirs(models_dir, exist_ok=True)

    csv_files = [file for file in os.listdir(data_dir) if file.endswith(".csv") and os.path.isfile(os.path.join(data_dir, file))]

    results = {} 

    for file in csv_files:
        try:
            pair_name = os.path.splitext(file)[0]
            file_path = os.path.join(data_dir, file)

            print(f"Processing {pair_name}...")

            df = pd.read_csv(file_path)

            if 'Time' not in df.columns or 'Close' not in df.columns:
                print(f"Error: {pair_name} missing required columns")
                continue

            df_prophet = pd.DataFrame({
                "ds": pd.to_datetime(df['Time']),
                "y": df["Close"]
            }).set_index("ds")["y"].resample("h").last().dropna().reset_index()

            model = Prophet(
                changepoint_prior_scale=0.01,
                daily_seasonality=False,
                weekly_seasonality=False
            )

            model.fit(df_prophet)
            anchor_to_last_close(model, df_prophet)

            model_path = os.path.join(models_dir, f"{pair_name}_model.pkl")
            joblib.dump(model, model_path)

            results[pair_name] = "Success"
            print(f"✅ Model for {pair_name} trained and saved successfully")

        except Exception as e:
            results[pair_name] = f"Error: {str(e)}"
            print(f"❌ Error processing {pair_name}: {e}")
    return results

if __name__ == "__main__":
    local_path = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.dirname(local_path)
    # optional args so the daily job can point at other folders: python model.py [data_dir] [models_dir]
    data_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root_path, "processed")
    models_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root_path, "models")
    results = create_and_save_models(data_dir, models_dir)
    print("\nTraining Results:")
    for pair, status in results.items():
        print(f"{pair}: {status}")