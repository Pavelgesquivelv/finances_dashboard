import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Intenta leer desde secrets de Streamlit Cloud
try:
    ALPHA_VANTAGE_KEY = st.secrets['ALPHA_VANTAGE_KEY']
    TWELVE_DATA_KEY = st.secrets['TWELVE_DATA_KEY']
except Exception:
    # Fallback a variables de entorno local
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
    TWELVE_DATA_KEY = os.getenv('TWELVE_DATA_KEY')
