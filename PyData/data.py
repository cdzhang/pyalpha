import tushare as ts
from PyUtils.common import lazy_property


class BaseData:
    def __init__(self, code, start, end, date_type='D'):
        self.code = code
        self.start = start
        self.end = end
        self.date_type = date_type

    @lazy_property
    def get_hist_data(self):
        return ts.get_hist_data(self.code, self.start, self.end, self.date_type)


