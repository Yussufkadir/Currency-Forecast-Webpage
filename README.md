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
#### Technology    Purpose
React         18UI framework with hooks
TypeScript    Type-safe development
Vite          Fast build tool and dev server
Material-UI   (MUI)Component library and theming
Recharts/Chart.js   Data visualization
