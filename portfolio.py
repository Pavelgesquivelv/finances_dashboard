import pandas as pd
import streamlit as st
import base64
import os

PORTFOLIO_FILE = "portfolio.csv"

def load_portfolio():
    # Primero intenta cargar desde el archivo secreto de Streamlit
    try:
        csv_b64 = st.secrets['PORTFOLIO_CSV_BASE64']
        import io
        csv_bytes = base64.b64decode(csv_b64)
        df = pd.read_csv(io.StringIO(csv_bytes.decode('utf-8')))
        return df
    except KeyError:
        # Si no existe el secreto, carga desde el archivo local
        if os.path.exists(PORTFOLIO_FILE):
            df = pd.read_csv(PORTFOLIO_FILE)
            return df
        else:
            st.error('No se encontraron datos de portafolio. Secreto no está bien configurado')

def save_portfolio(df):
    df.to_csv(PORTFOLIO_FILE, index=False)
