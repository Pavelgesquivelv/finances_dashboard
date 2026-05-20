import pandas as pd

PORTFOLIO_FILE = "portfolio.csv"

def load_portfolio():
    df = pd.read_csv(PORTFOLIO_FILE)
    return df

def save_portfolio(df):
    df.to_csv(PORTFOLIO_FILE, index=False)
