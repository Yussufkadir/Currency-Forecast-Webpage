# 📈 AI Powered Forex Application
A full-stack financial application featuring real-time forex rates and machine learning-powered price predictions across multiple currency pairs. 
Built with automated data pipelines and Prophet time series forecasting.

![Screen Recording 2025-10-19 at 08 58 07](https://github.com/user-attachments/assets/ed2035dd-4fe4-499d-8cb6-5c152f6b7735)

## 🌐 Live Demo
URL:[Application](https://currency-forecast-webpage-m527.vercel.app)

## ✨ Key Features
- 📊 Real-Time Exchange Rates — Live currency data with automatic updates
- 🤖 ML Price Predictions — Prophet-based forecasting with confidence intervals
- 💱 Multi-Currency Support — Track and predict 4 major currency pairs
- ⚙️ Automated Data Pipeline — Daily GitHub Actions job that downloads fresh data, cleans it, retrains the models and redeploys them
- 🧪 Backtested Model — Model setup chosen with a walk-forward backtest against a naive baseline
- 🎨 Modern UI/UX — Responsive design with dark/light theme support
- 📈 Historical Analysis — View trends and patterns across different timeframes

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ (latest recommended)
- Bun (latest version)
- uv for Python packages

### Installation
### 1. Clone the repository
```bash
git clone https://github.com/Yussufkadir/Currency-Forecast-Webpage.git
cd Currency-Forecast-Webpage
```

### 2. Set up the backend
```bash
cd backend
pip install -r requirements.txt
```

### 3. Set up the frontend
```bash
cd frontend
bun install
```

### 4. Run the Application
> [!NOTE]
> you need to split the terminals.
1. Run the backend
```bash
cd backend
uvicorn backend:app --reload
```
2. Run the frontend
``` bash
cd frontend
bun run dev
```
Visit http://localhost:5173 to see the application.(will be on frontend side.)

## 🏗️ Architecture
![Forex_app_architecture_design drawio](https://github.com/user-attachments/assets/65258927-31ee-4268-9401-7a89ddb4089b)

### Component Overview
#### Frontend Layer

- React + TypeScript interface with Material-UI components
- Real-time data updates via REST API calls
- Responsive charts and theme management

#### Backend Layer

- Core API (FastAPI on Render) — live exchange rates from exchangerate-api.com
- Prediction API (FastAPI on a Hugging Face Space) — serves the Prophet models
- The frontend is deployed on Vercel

#### Data Pipeline

- Ingestion — 1-minute candles from the Twelve Data API (`pipeline/download_data.py`)
- Cleaning — Duplicate, missing value, inconsistent candle and price spike handling with PySpark (`pipeline/transform.py`)
- Feature Engineering — Technical indicators (moving averages, Bollinger bands, ATR, RSI, MACD)
- Model Training — Prophet retraining on hourly closes (`backend/model.py`)
- Exploration — Jupyter notebooks for data analysis, statistical testing and model experiments

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
| --- | --- |
| React | 18UI framework with hooks |
| TypeScript | Type-safe development |
| Vite | Fast build tool and dev server |
| Material-UI | (MUI)Component library and theming |
| Recharts/Chart.js | Data visualization | 

### Backend 
| Technology | Purpose |
| --- | --- |
| Python 3.12+ | Core backend language |
| FastAPI | High-performance async API framework |
| Prophet | Time series forecasting model | 
| Pydantic | Data validation and settings | 
| httpx/requests | External API integration |

### Data&Ml Pipeline
| Technology | Purpose |
| --- | --- |
| Jupyter Notebook | Model experimentation and analysis |
| PySpark | Large-scale data processing | 
| Pandas | Data manipulation and analysis | 
| NumPy | Numerical computations | 
| Statsmodels | Statistical testing and validation| 
| Scikit-learn | Feature scaling in model experiments |
| GitHub Actions | Daily scheduled data and model update |
| Twelve Data API | 1-minute forex candles |

## 📊 Supported Currency Pairs
### Currently supporting predictions for 4 major forex pairs:

- 🇺🇸🇪🇺 EUR/USD — Euro to US Dollar
- 🇬🇧🇺🇸 GBP/USD — British Pound to US Dollar
- 🇺🇸🇨🇦 USD/CAD — US Dollar to Canadian Dollar
- 🇺🇸🇨🇭 USD/CHF — US Dollar to Swiss Franc

## 🔄 Data Pipeline Workflow
### A GitHub Actions workflow (`.github/workflows/daily-update.yml`) keeps the predictions fresh. It runs at 06:00 UTC Monday to Saturday:

1. Ingestion — Download the last 100 days of 1-minute candles for the 4 pairs from Twelve Data (weekend quotes outside the Sunday 17:00 - Friday 17:00 New York trading week are dropped)
2. Cleaning — Remove duplicate timestamps, forward fill missing values, drop inconsistent candles (Open/Close outside High-Low)
3. Outlier Removal — Remove single-candle price spikes, detected on 1-minute log returns with IQR fences
4. Feature Engineering — Calculate technical indicators on time-ordered data
5. Model Retraining — Fit Prophet on hourly closes and anchor the forecast to the last close
6. Deployment — Upload the new models to the Hugging Face Space, which restarts with them
7. Bookkeeping — Commit `pipeline/last_run.json` with the date range and last close of each pair

### Running the pipeline locally
```bash
pip install -r pipeline/requirements.txt
export TWELVE_DATA_API_KEY=<your key>
python pipeline/download_data.py raw --days 100
python pipeline/transform.py raw processed
python backend/model.py processed models
```
PySpark needs Java 17 (`JAVA_HOME` must point to it).

### Setting up the daily job on a fork
Add two repository secrets under Settings → Secrets and variables → Actions:
- `TWELVE_DATA_API_KEY` — a free key from [twelvedata.com](https://twelvedata.com)
- `HF_TOKEN` — a Hugging Face token with write access to the Space that serves the models

Then start the first run from the Actions tab with "Run workflow".

## 🧪 Model Evaluation
The Prophet setup was chosen with a walk-forward backtest (`research/backtest_prophet.py`): for each of the 4 pairs and each of the last 4 trading weeks of the historical data (Feb 24 - Mar 21, 2025), the model is trained on everything before Monday, forecasts the next 5 days and is scored every hour. Every setup is compared to a naive forecast that the price stays at the last close.

| Setup | MAPE % | Day 1 | Days 2-3 | Days 4-5 | Weeks beating naive (of 16) |
| --- | --- | --- | --- | --- | --- |
| Naive: last close | 0.636 | 0.242 | 0.614 | 0.872 | — |
| **Hourly, no weekly seasonality, anchored (current)** | **0.708** | **0.240** | **0.565** | 1.115 | 5 |
| Hourly, weekly seasonality, anchored | 0.765 | 0.250 | 0.626 | 1.194 | 6 |
| Minute data + ATR14/RSI14/MACD regressors | 0.914 | 0.596 | 0.718 | 1.298 | 4 |
| Minute data, weekly seasonality (previous model) | 0.923 | 0.604 | 0.724 | 1.309 | 4 |
| Hourly, trend follows recent data (changepoint_range 0.95) | 1.678 | 0.741 | 1.488 | 2.388 | 1 |

Full results: `research/backtest_summary.csv`.

What the backtest showed:
- **Anchoring** the forecast to the last close removes Prophet's level error at the start of the forecast (it was up to ~1.5%), which cuts the day 1 error from 0.60% to 0.24%.
- **Weekly seasonality** learned from ~14 weeks of data is mostly noise, turning it off helps.
- **Hourly data** is as accurate as minute data and trains in seconds instead of ~40 seconds per model.
- **Technical indicator regressors** do not help (<1% difference). Price level regressors (MA20, Bollinger bands) held at their last value only flatten the forecast into the naive one.
- Overall, the current setup is **23% more accurate than the previous model** and matches or beats the naive forecast for the first 3 days, but **no setup beats the naive forecast over 5 days**. Short-term exchange rates behave close to a random walk, so the confidence interval is the more useful part of the prediction.

`model.ipynb` is the earlier exploration log (minute data with regressors), the production setup lives in `backend/model.py`.

## 🤝 Contributing
### Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Prophet library by Meta for time series forecasting
- Historical data used for exploration and the backtest by [forexsoftware](https://forexsb.com/historical-forex-data) (compiled from Dukascopy tick data).
- Daily 1-minute data from [Twelve Data](https://twelvedata.com).
- Material-UI for the component library

## 📧 Contact
Yussufkadir Syurmen — [Linkedin](https://www.linkedin.com/in/yussufkadir-syurmen-b3306b22b/)  — syurmen2@gmail.com
Project Link: [Forex App](https://github.com/Yussufkadir/Currency-Forecast-Webpage).

> [!NOTE]
> This is a demonstration project. Predictions are for educational purposes only and should not be used for actual trading decisions.
