import streamlit as st
import pandas as pd
import plotly.express as px
from portfolio import load_portfolio
from data_fetcher import get_portfolio_value, get_usd_mxn_rate
from historical import compute_portfolio_history

# Mapeo: Nombres de Portafolios -> nombre base del archivo 
PORTFOLIO_MAP = {
    'Portafolio Principal': 'portfolio',
    'Portafolio Crypto': 'portfolio_2'
}

st.set_page_config(page_title="Mi Dashboard", layout="wide")

# --- Selector de portafolio ---
st.sidebar.title('Configuración')
# Selector de nombres de portafolios
friendly_names = list(PORTFOLIO_MAP.keys())
selected_name = st.sidebar.selectbox(
    'Selecciona el portafolio',
    friendly_names
)
selected_portfolio = PORTFOLIO_MAP[selected_name]
# Cargar portafolio
portfolio = load_portfolio(selected_portfolio)

st.title(f"📈 Dashboard de Portafolio de Inversiones - {selected_name.title()}")
st.sidebar.header("Posiciones actuales")
st.sidebar.dataframe(portfolio[['asset','quantity','currency']])

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

if selected_name == 'Portafolio Principal':
# --- Sección de Evolución histórica ---
    st.subheader(' 📅 Evolución del Portafolio (MXN)')

# Selector del periodo
    period = st.selectbox(
        'Selecciona el periodo:',
        options=['1mo','3mo','6mo','1y'],
        index=0
    )

# Cargar y cachear el histórico (para no repetir llamadas cada vez que se cambia el periodo)
    @st.cache_data(ttl=3600) # 1 hora de caché
    def load_history(portfolio, period):
        return compute_portfolio_history(portfolio, period)

    with st.spinner('Cargando históricos...'):
        hist_df = load_history(portfolio, period)

    # Gráfico de línea del valor total
    fig_line = px.line(
        hist_df,
        x='Date',
        y='Total_MXN',
        title=f'Evolución del valor del portafolio (último {period})',
        labels={'Total_MXN':'MXN'}
    )
    fig_line.update_layout(yaxis_tickprefix='$')
    st.plotly_chart(fig_line, width='stretch')

    # Optional mostrar tabla de de datos históricos
    with st.expander('Ver tabla de datos históricos'):
        st.dataframe(hist_df.style.format({'Total_MXN': '${:,.2f} MXN'}))

# Nota sobre limitaciones
#st.caption("Datos de acciones: Alpha Vantage (25 req/día gratis). Crypto: Binance API pública.")
