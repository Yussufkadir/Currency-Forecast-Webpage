# 📈 AI Powered Forex Application
A full-stack financial application featuring real-time forex rates and machine learning-powered price predictions across multiple currency pairs. 
Built with automated data pipelines and Prophet time series forecasting.

<img width="1408" height="684" alt="Screenshot 2025-10-06 at 20 42 10" src="https://github.com/user-attachments/assets/963f6c95-07d3-4527-b323-0c95701edbc8" />

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
`git clone https://github.com/yourusername/forex-app.git
cd forex-app`

### 2. Set up the backend
`cd backend
pip install -r requirements.txt`

### 3. Set up the frontend
`cd frontend
bun install`

### 4. Run the Application
> Note: you need to split the terminals.
1. Run the backend
`cd backend
uvicorn backend:app --reload`
2. Run the frontend
`cd frontend
bun run dev`
Visit http://localhost:5173 to see the application.(will be on frontend side.)

## 🛠️ Tech Stack

**Frontend:**
- React with TypeScript
- Vite
- MUI

**Backend:**
- Python
- FastAPI
- Prophet(Time series forecasting)

**Data Pipeline & ML:**
- Jupyter Notebook(Model experimentation and analysis)
- PySpark(Data processing)
- NumPy(Data manipulation)
- Pandas(Data manipulation)
- Statsmodels(Statistical testing and validation)

## 🏗️ Architecture
![Forex_app_architecture_design drawio](https://github.com/user-attachments/assets/65258927-31ee-4268-9401-7a89ddb4089b)

