from abc import ABCMeta, abstractmethod
import tushare as ts
from PyUtils.common import lazy_property
from glob import glob
import os
from PyData.config import HIST_DIR, HIST_END, HIST_START, TS_TOKEN
from PyData.utils import *

hist_file_ls = glob(os.path.join(HIST_DIR, '*.csv'))
ts.set_token(TS_TOKEN)
ts_pro = ts.pro_api()


class TuShareTool:
    @staticmethod
    def get_hist_ts(code, start, end, date_type):
        if isinstance(start, str):
            start = pd.to_datetime(start)

        if isinstance(end, str):
            end = pd.to_datetime(end)

        if start >= HIST_START and end <= HIST_END and glob(os.path.join(HIST_DIR, f'{code}*.csv')):
            file_dir = glob(os.path.join(HIST_DIR, f'{code}*.csv'))[0]
            df_hist = read_hist_csv(file_dir)
            df_hist = df_hist[(df_hist.date <= end) & (df_hist.date >= start)]
        else:
            df_hist = ts.get_hist_data(code, str(start), str(end), date_type).reset_index()
        return df_hist.sort_values('date', ascending=True)

    @staticmethod
    def get_tick_data(code, date):
        return ts.get_tick_data(code, date, src='tt')


class Stock(TuShareTool):
    def __init__(self, code, start, end, date_type='D'):
        self.code = code
        self.start = start
        self.end = end
        self.date_type = date_type

    @lazy_property
    def df_get_hist(self):
        return self.get_hist_ts(self.code, self.start, self.end, self.date_type)

    # @lazy_property
    # def get_industry(self):
    #     # todo add code2industry json file

    @lazy_property
    def df_get_close_return(self):
        """return list of daily return close price"""
        df = self.df_get_hist[['date', 'p_change', 'close', 'price_change']]
        p0 = df.close.iloc[0]
        df['cum_return'] = [(i - p0) / p0 for i in df.close]
        return df
