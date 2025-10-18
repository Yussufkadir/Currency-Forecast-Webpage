from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import requests
import asyncio
from dotenv import load_dotenv
from typing import Dict, Optional, Any, List
from contextlib import asynccontextmanager
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

MODEL_SERVICE_URL = os.environ.get("MODEL_SERVICE_URL")
MODEL_SERVICE_BASE = MODEL_SERVICE_URL.rstrip("/") if MODEL_SERVICE_URL else None

print(MODEL_SERVICE_URL)
print(MODEL_SERVICE_BASE)

model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

models: Dict[str, Any] = {}
available_pairs: List[str] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    load_models()
    yield
    print("Shutting down...")
    models.clear()

app = FastAPI(
    title="Forex prediction API",
    version="1.0.0",
    lifespan=lifespan
)
def load_models():
    global available_pairs
    if not os.path.exists(model_dir):
        print(f"There is no {model_dir} directory")
        return
    model_files = [f for f in os.listdir(model_dir) if f.endswith("_model.pkl")]

    for model_file in model_files:
        full_name = model_file.replace('_model.pkl', '')
        pair_name = (full_name
                     .replace('_M1_processed', '')
                     .replace('_processed', '')
                     .replace('_M1', '')
                     .upper())
        
        model_path = os.path.join(model_dir, model_file)
        models[pair_name] = joblib.load(model_path)

    available_pairs = list(models.keys())
    print(f"Loaded {len(models)} models: {', '.join(models.keys())}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
class PredictiononRequest(BaseModel):
    pair: str
    days: int=30

class PredictiononResponse(BaseModel):
    pair: str
    forecast: list
    dates: list
    lower_bound: list
    upper_bound: list

@app.get("/")
def read_root():
    return{"message": "App is running", "status": "healthy"}

@app.get("/api/pairs")
def get_available_pairs():
    if available_pairs:
        return {"pairs": available_pairs}
    return {"pairs": list(models.keys())}

# @app.post("/api/predict", response_model=PredictiononResponse)
# async def predict(request: PredictiononRequest):
    
#     pair = request.pair
#     days = min(request.days, 90)
#     logger.info(f"Received prediction request for {pair} for {days} days.")

#     if MODEL_SERVICE_BASE:
#         try:
#             async with httpx.AsyncClient(timeout=60.0) as client:
#                 response = await client.post(
#                     f"{MODEL_SERVICE_BASE}/predict",
#                     json=request.model_dump()
#                 )
#                 response.raise_for_status()
#                 data = response.json()
#                 logger.info("Forwarded prediction to remote model service for %s", pair)
#                 return data
#         except httpx.HTTPStatusError as exc:
#             logger.error("Remote model service returned error %s: %s", exc.response.status_code, exc.response.text)
#             raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#         except Exception as exc:
#             logger.error("Failed to reach remote model service: %s", exc)
#             raise HTTPException(status_code=502, detail="Unable to reach remote model service")

#     if pair not in models:
#         logger.error(f"Model for pair {pair} not found")
#         raise HTTPException(status_code=404, detail="This pair does not exist for the model")
    
#     model = models[pair]
    
#     try:
        
#         logger.info("Creating future dataframe...")
#         future = model.make_future_dataframe(periods=days)

#         logger.info("Making prediction...")       
#         forecast = model.predict(future)
#         logger.info("Prediction successful.")

#         forecast_values = forecast['yhat'].tail(days).tolist()
#         forecast_dates = [d.strftime("%Y-%m-%d") for d in forecast["ds"].tail(days).tolist()]
#         lower_bounds = forecast['yhat_lower'].tail(days).tolist()
#         upper_bounds = forecast['yhat_upper'].tail(days).tolist()

#         logger.info(f"Returning forecast data for {pair}.")
#         return {
#             "pair": pair,
#             "forecast": forecast_values,
#             "dates": forecast_dates,
#             "lower_bound": lower_bounds,
#             "upper_bound": upper_bounds
#         }
#     except Exception as e:
#         logging.error(f"Error occured in prediction for {pair}")
#         raise HTTPException(status_code=500, detail=f"An internal error occurred while making the prediction: {e}")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "models_loaded": len(models)}

# Live exchange rate functionality
async def get_live_exchange_rate(pair: str) -> Optional[Dict]:
    """
    Fetch live exchange rate for a currency pair
    """
    try:
        # Using exchangerate-api.com (free, no API key required)
        base_currency = pair[:3]  # e.g., 'EUR' from 'EURUSD'
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            target_currency = pair[3:]  # e.g., 'USD' from 'EURUSD'
            
            if target_currency in data['rates']:
                return {
                    'pair': pair,
                    'rate': data['rates'][target_currency],
                    'timestamp': datetime.now().isoformat(),
                    'source': 'exchangerate-api'
                }
    except Exception as e:
        logger.error(f"Error fetching live rate for {pair}: {e}")
        return None
    
EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest"
CURRENCY_API_BASE = "https://api.currencyapi.com/v3/latest"

live_rates_cache = {}
cache_timestamp = None
CACHE_DURATION = 300

@app.get("/api/live-rates")
async def get_live_rates():
    """
    Get current live exchange rate for a currency pair
    """
    global live_rates_cache, cache_timestamp

    try:
        current_time = datetime.now()
        if cache_timestamp and (current_time - cache_timestamp).total_seconds() < CACHE_DURATION:
            return {"live_rates": live_rates_cache}
        
        available_pairs_local = available_pairs if available_pairs else list(models.keys())
        live_rates = {}

        try:
            base_currencies = set()
            quote_currencies = set()

            for pair in available_pairs_local:
                if len(pair) >= 6:
                    base = pair[:3]
                    quote = pair[3:6]
                    base_currencies.add(base)
                    quote_currencies.add(quote)
            async with httpx.AsyncClient() as client:
                tasks = []
                for base in base_currencies:
                    tasks.append(fetch_rates_for_base(client, base))

                results = await asyncio.gather(*tasks, return_exceptions=True)

            all_rates = {}
            for result in results:
                if isinstance(result, dict):
                    all_rates.update(result)

            timestamp = datetime.now().isoformat()
            for pair in available_pairs_local:
                if len(pair) >= 6:
                    base = pair[:3]
                    quote = pair[3:6]

                    if base in all_rates and quote in all_rates[base]:
                        live_rates[pair] = {
                            "pair": pair,
                            "rate": all_rates[base][quote],
                            "timestamp": timestamp,
                            "source": "exchangerate-api.com"
                        }
                    else:
                        if base in all_rates and "USD" in all_rates[base] and quote in all_rates and "USD" in all_rates[quote]:
                            base_usd  = all_rates[base]["USD"]
                            quote_usd = all_rates[quote]["USD"]
                            cross_rate = base_usd / quote_usd
                            live_rates[pair] = {
                                "pair": pair,
                                "rate": cross_rate,
                                "timestamp": timestamp,
                                "source": "exchangerate-api.com (calculated)"
                            }
        except Exception as e:
            print(f"Error with exchangerate-api: {e}")
            timestamp = datetime.now().isoformat()
            mock_rates = {
                "EURUSD": 1.0850,
                "GBPUSD": 1.2650,
                "USDJPY": 149.50,
                "USDCHF": 0.8950,
                "AUDUSD": 0.6580,
                "USDCAD": 1.3720,
                "NZDUSD": 0.6120
            }

            for pair in available_pairs_local:
                if pair in mock_rates:
                    live_rates[pair] = {
                        "pair": pair,
                        "rate": mock_rates[pair] * (1 + np.random.normal(0, 0.001)),
                        "timestamp": timestamp,
                        "source": "mock data"
                    }

        live_rates_cache = live_rates
        cache_timestamp = current_time

        return {"live_rates": live_rates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching the live rates: {str(e)}")

@app.get("/api/live-rate/{pair}")
async def get_all_live_rate(pair: str):
    """
    Get live rates for all available currency pairs
    """
    try:
        rates_response = await get_live_rates()
        live_rates = rates_response["live_rates"]
        if pair not in live_rates:
            raise HTTPException(status_code=404, detail="This pair does not exist or live rate not available")
        return live_rates[pair]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching the live rate for {pair}: {str(e)}")
    
async def fetch_rates_for_base(client: httpx.AsyncClient, base_currency: str):
    try:
        url = f"{EXCHANGE_RATE_API}/{base_currency}"
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        return {base_currency: data.get("rates", {})}
    except Exception as e:
        print(f"Error fetching rates for base {base_currency}: {e}")
        return {}
    
@app.get("/api/rates-health")
async def rates_health():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXCHANGE_RATE_API}/USD", timeout=5.0)
            if response.status_code == 200:
                return {"status": "healthy", "service": "exchangerate-api.com"}
            else:
                return {"status": "degraded", "service": "API returning errors"}
    except Exception as e:
        return {"status": "unhealthy", "service": str(e)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)