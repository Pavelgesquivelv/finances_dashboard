import os
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
TWELVE_DATA_KEY = os.getenv('TWELVE_DATA_KEY')
