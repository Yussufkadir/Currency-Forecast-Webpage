from prophet import Prophet
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns
from prophet import Prophet
import sys
import os
import joblib
from sklearn.preprocessing import StandardScaler


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
            })    

            model = Prophet(
                changepoint_prior_scale=0.01,
                daily_seasonality=False,
                weekly_seasonality=True
            )

            model.fit(df_prophet)

            model_path = os.path.join(models_dir, f"{pair_name}_model.pkl")
            joblib.dump(model, model_path)

            results[pair_name] = "Success"
            print(f"✅ Model for {pair_name} trained and saved successfully")

        except Exception as e:
            results[pair_name] = f"Error: {str(e)}"
            print(f"❌ Error processing {pair_name}: {e}")
    return results

if __name__ == "__main__":
    data_dir = r"C:\Users\yusuf\OneDrive\Desktop\Forex Project\processed"
    models_dir = r"C:\Users\yusuf\OneDrive\Desktop\Forex Project\models"
    results = create_and_save_models(data_dir, models_dir)
    print("\nTraining Results:")
    for pair, status in results.items():
        print(f"{pair}: {status}")