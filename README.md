# 📈 AI Powered Forex Application

Full-stack financial forex application with automated ML pipeline for multi-currency prediction.

<img width="1408" height="684" alt="Screenshot 2025-10-06 at 20 42 10" src="https://github.com/user-attachments/assets/963f6c95-07d3-4527-b323-0c95701edbc8" />

## 🎯 Features

**Live Currency Exchange Rates** - real-time data integration
**ML-Powered Forecasts** - Prophet-based time series predictions
**Multi-Currency Support** - Supporting 4 currencies
**Automated Pipeline** - Self-updating data ingestion and cleaning
**Dark/Light Theme** - Customizable UI

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

┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│              (React + TypeScript + Vite)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (HTTP/JSON)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Live Rates   │  │ Predictions  │  │  Historical  │     │
│  │   Endpoint   │  │   Endpoint   │  │    Data      │     │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘     │
└─────────┼──────────────────┼──────────────────────────────┘
          │                  │
          │                  ▼
          │         ┌─────────────────┐
          │         │  Prophet Model  │
          │         │   (Forecasting) │
          │         └────────▲────────┘
          │                  │
          ▼                  │
┌──────────────────────────┐ │
│   External Forex API     │ │
│   (Real-time Rates)      │ │
└──────────────────────────┘ │
                             │
          ┌──────────────────┴──────────────────┐
          │        Automated Data Pipeline       │
          │  ┌────────────────────────────────┐ │
          │  │  1. Data Ingestion             │ │
          │  │     (API polling & storage)    │ │
          │  └────────────┬───────────────────┘ │
          │               ▼                      │
          │  ┌────────────────────────────────┐ │
          │  │  2. Data Cleaning              │ │
          │  │     (PySpark + Pandas)         │ │
          │  └────────────┬───────────────────┘ │
          │               ▼                      │
          │  ┌────────────────────────────────┐ │
          │  │  3. Feature Engineering        │ │
          │  │     (Technical indicators)     │ │
          │  └────────────┬───────────────────┘ │
          │               ▼                      │
          │  ┌────────────────────────────────┐ │
          │  │  4. Model Training             │ │
          │  │     (Jupyter + Prophet)        │ │
          │  └────────────────────────────────┘ │
          └─────────────────────────────────────┘
