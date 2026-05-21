import pandas as pd
import yfinance as yf
import requests
import time


def _remove_timezone(index):
    """ Convierte el índice a UTC y luego elimina la zona horaria... """
    if index.tz is not None:
        index = index.tz_convert('UTC').tz_localize(None)
    return index

def get_equity_history(symbol, period='1mo'):
    """ Descarga el histórico de una acción vía yfinance """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        if data.empty:
            raise ValueError(f'No se encontraron datos históricos para {symbol}')
        data.index = _remove_timezone(data.index)
        return data['Close']
    except Exception as e:
        print(f'Error en get_equity_history({symbol}): {e}')
        return pd.Series(dtype=float)   # Serie vacía
    
def get_crypto_history(symbol, period='1mo'):
    '''
    Obtiene velas diarias de Binance y devuelve una serie de precios de cierre
    symbol: ej "BTCUSDT"
    period: "1mo", "3mo" -> lo convertiremos a días
    '''
    
    # Convertir periodo a número de días
    days_map = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730}
    limit = days_map.get(period, 30)

    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol.upper(),
        'interval': '1d',
        'limit': limit
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    klines = resp.json()

    # Cada vela: [open_time, open, high, low, close, volume, ...]
    dates = pd.to_datetime([k[0] for k in klines], unit='ms')
    closes = [float(k[4]) for k in klines]
    return pd.Series(closes, index=dates)

def get_usd_mxn_history(period='1mo'):
    """ Tipo de cambio diario USD/MXN de yahoo finance """
    ticker = yf.Ticker('MXN=X')
    data = ticker.history(period=period)
    if data.empty:
        raise ValueError('No se pudo obtener el histórico del TC USD/MXN')
    data.index = _remove_timezone(data.index)
    return data['Close']

def compute_portfolio_history(portfolio_df, period='1mo', include_crypto=True):
    """
      Calcula la evolución diario del valor total del portafolio en MXN 
      portfolio_df: DataFrame con cols [asset, symbol, quantity, type, currency]
      period: '1mo', '3mo', '6mo', '1y'
      """
    fx = get_usd_mxn_history(period)

    # DataFrame acumulador con el índice de fechas en común
    combined = pd.DataFrame(index=fx.index)
    combined['Cash_MXN'] = 0.0 # Col efectivo

    for _, row in portfolio_df.iterrows():
        symbol = row['symbol']
        qty = float(row['quantity'])
        asset_type = row['type']
        currency = row['currency']
        asset_name = row['asset']

        # Efectivo
        if asset_type == 'cash':
            # Valor cte para cada día
            combined['Cash_MXN'] += qty
            continue
        
        # Obtener precios históricos
        prices = None
        try:
            if asset_type == 'equity':
                # Usamos yfinance para todos los equities
                prices = get_equity_history(symbol, period)
            elif asset_type == 'crypto':
                if include_crypto:
                    prices = get_crypto_history(symbol, period)
                else:
                    continue
            else:
                continue
        except Exception as e:
            print(f'No se pudo obtener historia de {symbol}: {e}')
            continue
        # Verificar que prices sea una Serie válida
        if prices is None or prices.empty:
            print(f'Histórico vacío o nulo para {symbol}, se omite.')
            continue
        #prices = prices.reindex(fx.index)
        #prices.bfill(inplace=True)
        #prices.ffill(inplace=True)
        
        # Convertimos a MXN si está en USD, por el momento es la única conversión disponible
        if currency == 'USD':
            # Alinear fechas: reindexar la serie de precios para que coincida con el índice del FX
            prices = prices.reindex(fx.index, method='ffill')
            # Convertir usando el tipo de cambio correspondiente
            values_mxn = prices * fx * qty
        else: # MXN
            prices = prices.reindex(fx.index, method='ffill')
            values_mxn = prices * qty

        # Añadir al df combinado
        combined[asset_name] = values_mxn

    # Sumamos todas las cols para obtener el total diario
    combined.bfill(inplace=True)
    combined.ffill(inplace=True)
    combined['Total_MXN'] = combined.sum(axis=1)

    # Excluimos la columns 'Cash_MXN' y 'Total_MXN'
    investment_cols = [col for col in combined.columns if col not in ['Cash_MXN', 'Total_MXN']]
    if investment_cols:
        # Crear una máscara booleana: True donde al menos un activo tiene valor
        has_investment = combined[investment_cols].notna().any(axis=1)
        # Encontrar la primer posición con True
        first_valid_pos = has_investment.idxmax()

        #first_valid_idx = combined[investment_cols].notna().any(axis=1).idxmax()
        # Cortar desde esa fecha en adelante
        if has_investment.any():
            combined = combined.loc[first_valid_pos:]

    combined.index.name = 'Date'
    return combined.reset_index()
