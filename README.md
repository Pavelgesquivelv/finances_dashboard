# # 📈 Financial Dashboard Equity & Crypto

Interactive Dashboard for Equities and Crypto Portfolios

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.30+-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/deploy-Streamlit%20Cloud-orange.svg" alt="Deployment">
</p>

## Características

- ** Real time prices ** 
- ** All prices converted to MXN with the latest currency USD/MXN rate
- ** Three different types of Portfolios (Equity Mex, Equity USA y Crypto)
- ** Historical graphics (1 mes, 3 meses, 6 meses y 1 año)
- ** Deployed via Streamlit with secrets... (portafolios)

## Technologies and APIs

|Component | API / Lib |
|-----------|----------------|
|Equity México | Yahoo Finance |
|Equity USA | Twelve Data |
|Crypto (precios live) | CoinGecko (public API) |
|rate USD/MXN | Yahoo Finance ('MXN=X') |
|Interface and graphics | Streamlit + Plotly |
|Data | Pandas |

## The Project

finances_dashboard/
|- dashboard.py # Main app with user interface
|- config.py # Loads environment variables and secrets
|- data_fetcher.py # Fetches current prices (Twelve Data, Yahoo Finance, CoinGecko)
|- historical.py # Computes portfolio's historical performances
|- portfolio.py # Portfolio loading and management logic (CSV / secrets)
|- portfolio.csv.example # Example portfolio file
|- requirements.txt # Project dependencies
|- README.md # This document

## url
https://financesdashboard-zbvrud56ahgwar2adxkmyy.streamlit.app/
