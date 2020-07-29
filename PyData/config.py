import os
from datetime import datetime

HIST_DIR = os.path.join(os.path.dirname(__file__), 'hist_data')
HIST_START = datetime(year=2005, day=1, month=1)
HIST_END = datetime(year=2020, day=28, month=7)
TS_TOKEN = os.getenv('TS_TOKEN', '7dd7dc496ee9de8e4c8052e54ec22ac23f8f1ad8b05aa42603a1e472')
STOCK_JSON = os.path.join(HIST_DIR, 'stock_basic.json')
