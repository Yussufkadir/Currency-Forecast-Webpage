from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Forex Prediction API")


## we need to use CORS middleware to connect frontent to fastapi backend
app.add_middleware(
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
    logger.info(f"Received prediction request for {pair} for {days} days.")

    if pair not in models:
        logger.error(f"Model for pair {pair} not found")
        raise HTTPException(status_code=404, detail="This pair does not exist for the model")
    
    model = models[pair]
    
    try:
        
        logger.info("Creating future dataframe...")
        future = model.make_future_dataframe(periods=days)

        logger.info("Making prediction...")       
        forecast = model.predict(future)
        logger.info("Prediction successful.")

        forecast_values = forecast['yhat'].tail(days).tolist()
        forecast_dates = [d.strftime("%Y-%m-%d") for d in forecast["ds"].tail(days).tolist()]
        lower_bounds = forecast['yhat_lower'].tail(days).tolist()
        upper_bounds = forecast['yhat_upper'].tail(days).tolist()

        logger.info(f"Returning forecast data for {pair}.")
        return {
            "pair": pair,
            "forecast": forecast_values,
            "dates": forecast_dates,
            "lower_bound": lower_bounds,
            "upper_bound": upper_bounds
        }
    except Exception as e:
        logging.error(f"Error occured in prediction for {pair}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred while making the prediction: {e}")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "models_loaded": len(models)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)