from abc import ABCMeta, abstractmethod
import tushare as ts
from PyUtils.common import lazy_property
from glob import glob
import os
from PyData.config import HIST_DIR, HIST_END, HIST_START, TS_TOKEN, STOCK_JSON
from PyData.utils import *
import math
import json

hist_file_ls = glob(os.path.join(HIST_DIR, '*.csv'))
ts.set_token(TS_TOKEN)
ts_pro = ts.pro_api()

# stock_json = json.loads(open(STOCK_JSON).read(), encoding='utf8')
with open(STOCK_JSON, encoding='utf-8') as data_file:
    stock_json = json.load(data_file)


class TuShareTool:
    @staticmethod
    def _get_hist_ts(code, start, end):
        if isinstance(start, str):
            start = pd.to_datetime(start)

        if isinstance(end, str):
            end = pd.to_datetime(end)

        if start >= HIST_START and end <= HIST_END and glob(os.path.join(HIST_DIR, f'{code}*.csv')):
            print('local disk code', code)
            file_dir = glob(os.path.join(HIST_DIR, f'{code}*.csv'))[0]
            df_hist = read_hist_csv(file_dir)
            df_hist = df_hist[(df_hist.date <= end) & (df_hist.date >= start)]
        else:
            # print('API code', code)
            df_hist = ts_pro.daily(ts_code=code, start_date=start.strftime('%Y%m%d'), end_date=end.strftime('%Y%m%d'))
            df_hist['date'] = df_hist['trade_date'].apply(pd.to_datetime)
        return df_hist.sort_values('date', ascending=True)

    @staticmethod
    def _get_tick_data(code, date):
        return ts.get_tick_data(code, date, src='tt')


class Stock(TuShareTool):
    def __init__(self, code, start, end, date_type='D'):
        self.code = code
        self.start = start
        self.end = end
        self.date_type = date_type
        # self.industry = stock_json[code][]

    @lazy_property
    def df_get_hist(self):
        df_hist = self._get_hist_ts(self.code, self.start, self.end)
        df_hist['log_return'] = df_hist['pct_chg'].apply(lambda x: math.log(x/100 + 1))
        return df_hist

    @lazy_property
    def get_market_date_list(self):
        return self.df_get_hist['date'].tolist()

    # @lazy_property
    # def get_industry(self):
    #     # todo add code2industry json file

    @lazy_property
    def df_get_close_return(self):
        """return list of daily return close price"""
        df = self.df_get_hist[['date', 'pct_chg', 'close', 'change']]
        p0 = df.close.iloc[0]
        df['cum_return'] = [(i - p0) / p0 for i in df.close]
        return df
