import requests
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from config import ALPHA_VANTAGE_KEY, TWELVE_DATA_KEY
from twelvedata import TDClient
import time
import yfinance as yf

# Cliente único de Twelve Data
td = TDClient(apikey=TWELVE_DATA_KEY)

# --------------- TIPOS DE CAMBIO ------------
def get_usd_mxn_rate():
    """ Devuelve el tipo de cambio USD/MXN actual usando yfinance """
    try:
        ticker = yf.Ticker('MXN=X')
        data = ticker.history(period='1d')
        if not data.empty:
            rate = data['Close'].iloc[-1]
            return rate
        else:
            # Fallback intentamos con info
            info = ticker.info
            return info.get('regularMarketPrice', 18.0) # Valor por default razonable
    except Exception:
        # If everything fails!
        print('No se pudo obtener tipo de cambio USD/MXN, usando valor fijo de 18.0')
        return 18.0
    
        

#----------------Equity (Alpha)
#def get_equity_price(symbol):
#    """ Devuelve el último precio de una acción """
#    ts = TimeSeries(key=ALPHA_VANTAGE_KEY, output_format='pandas')
#    data, meta = ts.get_quote_endpoint(symbol=symbol)
#    price = float(data['05. price'].iloc[0])
#    change_pct = data['10. change percent'].iloc[0]
#    return price, change_pct

# ---------------- Equity TwelveData (MEX & USA) -----------------
def get_equity_price(symbol):
    try:
        quote = td.quote(symbol=symbol).as_json()
        price = float(quote['close'])
        change_pct = quote['percent_change']
        return price, f'{change_pct}%'
    except Exception as e:
        print(f'TwelveData falló para {symbol}: {e}')
        # Fallback a yfinance para los assets Mexicanos
        raise

# --- Función para cryptos... ---
def get_crypto_price(symbol):
    try:
        # Primero Binance
        return get_crypto_price_binance(symbol)
    except Exception as e:
        print(f'Binance falló ({e}), usando CoinGecko API as backup...')
        return get_crypto_price_coingecko(symbol)
# ----------------- Crypto (Binance)
def get_crypto_price_binance(symbol):
    """ Devuelve precio actual y cambio 24h de un en Binance
     con reintentos y headesr para evitar bloqueos en la nube
       """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    base_price_url = "https://api.binance.com/api/v3/ticker/price"
    base_24h_url = "https://api.binance.com/api/v3/ticker/24hr"
    symbol_upper = symbol.upper()

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Precio actual
            price_resp = requests.get(
                base_price_url,
                params={"symbol": symbol_upper},
                headers=headers,
                timeout=10
            )
            price_resp.raise_for_status()
            price_data = price_resp.json()
            price = float(price_data['price'])

            # Estadísticas 24h
            stats_resp = requests.get(
                base_24h_url,
                params={"symbol": symbol_upper},
                headers=headers,
                timeout=10
            )
            stats_resp.raise_for_status()
            stats = stats_resp.json()
            change_pct = float(stats['priceChangePercent'])
            return price, f"{change_pct}%"

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise e

_coingecko_cache = None
_coingecko_cache_time = 0

def get_all_crypto_prices_coingecko(symbols):
    """ Obtiene precios y cambios 24h de MULTIPLES cryptos en una sola llamada
      desde CoinGecko (API gratuita sin límites estrictos)"""
    global _coingecko_cache, _coingecko_cache_time
    # Usar caché si la última llamada fue hace menos de 60 segundos
    now = time.time()
    if _coingecko_cache and (now - _coingecko_cache_time) < 60:
        return _coingecko_cache
    # Mapeo de símbolos de Binance a IDs de CoinGecko
    mapping = {
        'BTCUSDT': 'bitcoin',
        'ETHUSDT': 'ethereum',
        'XRPUSDT': 'ripple',
        'BNBUSDT': 'binancecoin',
        'LTCUSDT': 'litecoin',
        'XCHUSDT': 'chia',
        'POLUSDT': 'polygon-ecosystem-token', 
        'BTTUSDT': 'bittorrent',
        'ADAUSDT': 'cardano',
        'AVAXUSDT': 'avalanche-2',
        'BCHUSDT': 'bitcoin-cash',
        'DOTUSDT': 'polkadot',
        'TRXUSDT': 'tron',
        'MANAUSDT': 'decentraland',
        'BATUSDT': 'basic-attention-token',
        'LINKUSDT': 'chainlink',
        'XLMUSDT': 'stellar',
        'SOLUSDT': 'solana'
    }
    ids = []
    for sym in symbols:
        coin_id = mapping.get(sym.upper())
        if coin_id:
            ids.append(coin_id)

    if not ids:
        return {}
    
    # Una sola llamda por todos los IDs
    url = f'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': ','.join(ids),
        'vs_currencies': 'usd',
        'include_24hr_change': 'true'
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        # Diccionario de resultados
        results = {}
        for sym in symbols:
            coin_id = mapping.get(sym.upper())
            if coin_id and coin_id in data:
                price = data[coin_id]['usd']
                change_pct = data[coin_id].get('usd_24h_change', 0)
                results[sym.upper()] = (price, f'{change_pct:.2f}%')
            else:
                results[sym.upper()] = (0, '0%')

        # Guardar en caché
        _coingecko_cache = results
        _coingecko_cache_time = now

        return results
    
    except Exception as e:
        print(f'Error en la llamada batch a CoinGecko: {e}')
        return {}
    
def get_mexican_price(symbol):
    """ Obtiene el precio actual y cambio % diario de un activo MX """
    ticker = yf.Ticker(symbol)
    data = ticker.history(period='1d')
    if data.empty:
        raise ValueError(f'No se puedo obtener datos para {symbol}')
    last_close = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[0]
    info = ticker.info
    prev_close = info.get('previousClose', prev_close)
    change_pct = ((last_close - prev_close) / prev_close) * 100
    return last_close, f'{change_pct:.2f}%'

def get_portfolio_value(portfolio_df):
    """ Añade cols de precio, valor y cambio % de cada activo """
    # Primero, todos los precios crypto de una sola vez
    crypto_symbols = portfolio_df[portfolio_df['type'] == 'crypto']['symbol'].unique()
    crypto_prices = {}
    if len(crypto_symbols) > 0:
            crypto_prices = get_all_crypto_prices_coingecko(crypto_symbols)

    rows = []
    for _, row in portfolio_df.iterrows():
        symbol = row['symbol']
        qty = float(row['quantity'])
        asset_type = row['type']

        if asset_type == 'cash':
            rows.append({
                'asset': row['asset'],
                'symbol': symbol,
                'quantity': qty,
                'type': 'cash',
                'currency': row['currency'],
                'price': 1.0,
                'value': qty,
                'change_24h': '0%'
            })
            continue

        try:
            if asset_type == 'equity':
                if symbol.endswith('.MX'):
                    price, change_pct = get_mexican_price(symbol)
                else:
                    price, change_pct = get_equity_price(symbol)
                    time.sleep(1.5)
            elif asset_type == 'crypto':
                if symbol.upper() in crypto_prices:
                    price, change_pct = crypto_prices[symbol.upper()]
                else:
                    price, change_pct = 0, '0%'
                #price, change_pct = get_crypto_price_coingecko(symbol)
        except Exception as e:
            print(f'Error fetching {symbol}: {e}')
            price, change_pct = 0, '0%'

        total_value = price * qty
        rows.append({
            'asset': row['asset'],
            'symbol': symbol,
            'quantity': qty,
            'currency': row['currency'],
            'type': asset_type,
            'price': price,
            'value': total_value,
            'change_24h': change_pct
        })
    return pd.DataFrame(rows)
