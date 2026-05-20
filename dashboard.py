import streamlit as st
import pandas as pd
import plotly.express as px
from portfolio import load_portfolio
from data_fetcher import get_portfolio_value, get_usd_mxn_rate

st.set_page_config(page_title="Mi Dashboard Financiero", layout="wide")
st.title("📈 Dashboard de Inversiones (Alpha Vantage + Binance)")

# Cargar portafolio
portfolio = load_portfolio()
st.sidebar.header("Posiciones actuales")
st.sidebar.dataframe(portfolio)

# Obtener datos actualizados
with st.spinner("Obteniendo precios en tiempo real..."):
    df_value = get_portfolio_value(portfolio)

# ----- Conversión a MXN -----
rate = get_usd_mxn_rate()
st.sidebar.metric("Tipo de cambio USD/MXN", f"${rate:,.2f}")

# Añadimos columnas en MXN
df_value['price_mxn'] = df_value.apply(
    lambda row: row['price'] if row.get('currency') == 'MXN' else row['price'] * rate,
    axis=1
)
df_value['value_mxn'] = df_value.apply(
    lambda row: row['value'] if row.get('currency') == 'MXN' else row['value'] * rate,
    axis=1
)

# Métricas principales
total_equity = df_value[df_value['type'] == 'equity']['value_mxn'].sum()
total_crypto = df_value[df_value['type'] == 'crypto']['value_mxn'].sum()
total_cash = df_value[df_value['type'] == 'cash']['value_mxn'].sum()
total_portfolio = total_equity + total_crypto + total_cash

col1, col2, col3 = st.columns(3)
col1.metric("Renta Variable", f"${total_equity:,.2f} MXN")
col2.metric("Criptomonedas", f"${total_crypto:,.2f} MXN")
col3.metric("Total Portafolio", f"${total_portfolio:,.2f} MXN")

# Tabla detallada
st.subheader("Desglose por activo")
st.dataframe(
    df_value[['asset', 'quantity', 'currency', 'price', 'price_mxn', 'value_mxn', 'change_24h']].style.format({
        'quantity': '{:,.2f}',
        'price': lambda x: '${:,.2f}'.format(x) if x != 1 else 'N/A',
        'price_mxn': '${:,.2f} MXN',
        'value_mxn': '${:,.2f} MXN',
    }),
    width='stretch'
)

# Gráfico de distribución
fig_pie = px.pie(
    df_value, values='value_mxn', names='asset', title='Distribución del portafolio'
)
st.plotly_chart(fig_pie, width='stretch')

# Gráfico de barras de rentabilidad diaria
fig_bar = px.bar(
    df_value,
    x='asset',
    y='value_mxn',
    color='type',
    title='Valor actual por activo',
    text='value_mxn'
)
fig_bar.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
st.plotly_chart(fig_bar, width='stretch')

# Nota sobre limitaciones
st.caption("Datos de acciones: Alpha Vantage (25 req/día gratis). Crypto: Binance API pública.")
