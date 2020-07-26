import os
from datetime import datetime

HIST_DIR = os.path.join(os.path.dirname(__file__), 'hist_data')
HIST_START = datetime(year=2018, day=1, month=1)
HIST_END = datetime(year=2020, day=13, month=7)
TS_TOKEN = os.getenv('TS_TOKEN')
STOCK_JSON = os.path.join(HIST_DIR, 'stock_basic.json')
