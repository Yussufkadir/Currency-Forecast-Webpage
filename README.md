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
- ⚙️ Automated Data Pipeline — Self-updating ingestion, cleaning, and feature engineering
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
git clone https://github.com/yourusername/forex-app.git
cd forex-app
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

- FastAPI endpoints for live rates, predictions, and historical data
- Prophet ML model integration for forecasting
- External API integration for real-time forex data

#### Data Pipeline

- Ingestion — Automated fetching from forex data sources
- Cleaning — Data validation and preprocessing with PySpark
- Feature Engineering — Technical indicators and transformations
- Model Training — Jupyter-based experimentation and Prophet retraining

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
|Python 3.9+ | Core backend language | 
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
| Scikit-learn | Model evaluation metrics | 

## 📊 Supported Currency Pairs
### Currently supporting predictions for 4 major forex pairs:

- 🇺🇸🇪🇺 EUR/USD — Euro to US Dollar
- 🇬🇧🇺🇸 GBP/USD — British Pound to US Dollar
- 🇺🇸🇯🇵 USD/JPY — US Dollar to Japanese Yen
- 🇺🇸🇨🇭 USD/CHF — US Dollar to Swiss Franc

## 🔄 Data Pipeline Workflow
### The automated pipeline runs on a scheduled basis to keep predictions fresh:

1. Ingestion — Fetch latest forex data from external API every hour
2. Validation — Check for missing values, outliers, and data quality issues
3. Cleaning — Handle gaps, remove duplicates, normalize timestamps
4. Feature Engineering — Calculate technical indicators (moving averages, volatility, etc.)
5. Model Retraining — Update Prophet models with new data (daily)
6. Deployment — Replace production models with improved versions

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
- Forex data provided by [forexsoftware](https://forexsb.com/historical-forex-data).
- Material-UI for the component library

## 📧 Contact
Yussufkadir Syurmen — [Linkedin](https://www.linkedin.com/in/yussufkadir-syurmen-b3306b22b/)  — syurmen2@gmail.com
Project Link: [Forex App](https://github.com/yourusername/forex-app).

> [!NOTE]
> This is a demonstration project. Predictions are for educational purposes only and should not be used for actual trading decisions.
