from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import pandas as pd
from datetime import datetime, timedelta

app = FastAPI(title="Forex Prediction API")


## we need to use CORS middleware to connect frontent to fastapi backend
app.middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

model_dir = r"C:\Users\yusuf\OneDrive\Desktop\Forex Project\models"

models = {}

@app.on_event("startup")
def load_model():
    if not os.path.exists(model_dir):
        print(f"There is no {model_dir} directory")
        return
    
    model_files = [f for f in os.listdir(model_dir) if f.endswith('_model.pkl')]

    for model_file in model_files:
        pair_name = model_file.split('_model.pkl')[0]

        model_path = os.path.join(model_dir, model_file)
        models[pair_name] = joblib.load(model_path)

    print(f"Loaded {len(models)} models: {', '.join(models.keys())}")

class PredictiononRequest(BaseModel):
    pair: str
    days: int=30

class PredictiononResponse(BaseModel):
    pair: str
    forecast: list
    dates: list
    lower_bound: list
    upper_bound: list

@app.get("/api/pairs")
def get_available_pairs():
    return {"pairs": list(models.keys())}

@app.post("/api/predict", response_model=PredictiononResponse)
def predict(request: PredictiononRequest):
    
    pair = request.pair
    days = min(request.days, 90)

    if pair not in models:
        raise HTTPException(status_code=404, detail="This pair does not exist for the model")
    
    model = models[pair]
    
    future = model.make_future_dataframe(period=days)

    forecast = model.predict(future)

    forecast_values = forecast['yhat'].tail(days).tolist()
    forecast_dates = [d.strftime("%Y-$m-$d") for d in forecast["ds"].tail(days).tolist()]
    lower_bounds = forecast['yhat_lower'].tail(days).tolist()
    upper_bounds = forecast['yhat_upper'].tail(days).tolist()

    return {
        "pair": pair,
        "forecast": forecast_values,
        "dates": forecast_dates,
        "lower_bound": lower_bounds,
        "upper_bound": upper_bounds
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok", "models_loaded": len(models)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)