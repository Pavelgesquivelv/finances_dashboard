import pandas as pd
import streamlit as st
import base64
import os

def load_portfolio(portfolio_name):

    filename = f'{portfolio_name}.csv'
    secret_key = f'{portfolio_name.upper()}_CSV_BASE64'

    # Primero intenta cargar desde el archivo secreto de Streamlit Cloud de forma segura
    try:
        if hasattr(st, 'secrets') and st.secrets:
            csv_b64 = st.secrets[secret_key]
            if csv_b64:
                import io
                csv_bytes = base64.b64decode(csv_b64)
                df = pd.read_csv(io.StringIO(csv_bytes.decode('utf-8')))
                return df
    except Exception:
        pass
    
    # Si no existe el secreto, carga desde el archivo local
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        return df

    # 3. Si nada funciona, mostrar error y devolver vacío
    st.error(f"No se encontró el portafolio '{portfolio_name}'. "
             f"Verifica que el archivo {filename} exista localmente "
             f"o que el secreto {secret_key} esté configurado en Streamlit Cloud.")
    return pd.DataFrame()