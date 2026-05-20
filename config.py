import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_secret(key, default=None):
    """ Intenta leer desde secrets de Streamlit Cloud con fallback seguro """
    try:
        # Accedemos a st.secrets solo si existe
        if hasattr(st, 'secrets') and st.secrets:
            return st.secrets.get(key, default)
        else:
            return default
    except Exception:
        return default
    
ALPHA_VANTAGE_KEY = get_secret('ALPHA_VANTAGE_KEY') or os.getenv('ALPHA_VANTAGE_KEY')
TWELVE_DATA_KEY = get_secret('TWELVE_DATA_KEY') or os.getenv('TWELVE_DATA_KEY')
