import tushare as ts
from PyUtils.common import lazy_property
from glob import glob
import os
from PyData.config import HIST_DIR, HIST_END, HIST_START
from PyData.utils import *

hist_file_ls = glob(os.path.join(HIST_DIR, '*.csv'))


class SingleSecurity:
    def __init__(self, code, start, end, date_type='D'):
        self.code = code
        self.start = start
        self.end = end
        self.date_type = date_type

    @lazy_property
    def get_hist_data(self):
        if pd.to_datetime(self.start) >= HIST_START and pd.to_datetime(self.end) <= HIST_END and glob(
                os.path.join(HIST_DIR, f'{self.code}*.csv')):
            file_dir = glob(os.path.join(HIST_DIR, f'{self.code}*.csv'))[0]
            df_hist = read_hist_csv(file_dir)
        else:
            df_hist = ts.get_hist_data(self.code, self.start, self.end, self.date_type)
        return df_hist

    @lazy_property
    def get_industry(self):
        return ts.get_industry_classified('sw')

