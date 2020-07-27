# -*- coding: UTF-8 -*-

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from glob import glob


# # daily data filename, todo change it to db.table later
# filename = 'data/raw/daily_0715/daily_300143.SZ_v20200715.csv'
#
# df = pd.read_csv(filename)
# print(df.head())


class FeatBasic:
    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_csv(filename)
        # self.df.trade_date = pd.to_datetime(self.df.trade_date,
        #                                     format='%Y%m%d',
        #                                     errors='coerce')
        self.df = self.df.sort_values(by=['trade_date'], ascending=True)
        self.df = self.df.assign(ind=range(len(self.df)))

        self.df_moneyflow = pd.read_csv('data/raw/moneyflow_hsgt_0719.csv')
        self.df_moneyflow = self.df_moneyflow.sort_values(by=['trade_date'], ascending=True)
        self.df_moneyflow = self.df_moneyflow.assign(ind=range(len(self.df_moneyflow)))

    def _apply_time_window(self, trade_date, win=5, money_flow=False):

        """
        :param trade_date: 20180706, trade_date should be valid!todo change it
        :param win: int, e.g. 过去5个交易日
        :return: df
        """
        if money_flow is False:
            try:
                end_ind = self.df.loc[self.df['trade_date'] == trade_date].ind.values[0]
                begin_ind = max([0, end_ind - win])
                df_sub = self.df.loc[(self.df['ind'] < end_ind)
                                     &
                                     (self.df['ind'] >= begin_ind)]
                return df_sub
            except KeyError:
                return None
        if money_flow:
            try:
                # todo check 开市日历
                if trade_date in self.df_moneyflow.trade_date.values:
                    end_ind = self.df_moneyflow.loc[self.df_moneyflow['trade_date'] == trade_date].ind.values[0]
                    begin_ind = max([0, end_ind - win])
                    df_sub = self.df_moneyflow.loc[(self.df_moneyflow['ind'] < end_ind)
                                                   &
                                                   (self.df_moneyflow['ind'] >= begin_ind)]
                    return df_sub
                else:
                    return None
            except KeyError:
                return None

    def __div(self, a, b):
        if b == 0:
            return None
        return a/b

    def __norm_val(self, val, vals_norm, colname):
        return self.__div(val - vals_norm[colname]['min'],
                          (vals_norm[colname]['max'] - vals_norm[colname]['min']))

    def __abs_feat_stat_last_n_days(self, trade_date, win):
        df_sub = self._apply_time_window(trade_date, win)

        vals_norm = dict()
        for colname in ['high', 'low', 'open', 'close',
                        'change', 'vol', 'amount']:
            vals_norm[colname] = {'min': np.nanmin(df_sub[colname]),
                                  'max': np.nanmax(df_sub[colname])}

        feat = dict()
        feat['max_{}_win_{}'.format('pct_chg', win)] = np.nanmax(df_sub['pct_chg'].values)
        feat['min_{}_win_{}'.format('pct_chg', win)] = np.nanmin(df_sub['pct_chg'].values)
        feat['mean_{}_win_{}'.format('pct_chg', win)] = np.nanmean(df_sub['pct_chg'].values)
        feat['median_{}_win_{}'.format('pct_chg', win)] = np.nanmedian(df_sub['pct_chg'].values)
        feat['std_{}_win_{}'.format('pct_chg', win)] = np.nanstd(df_sub['pct_chg'].values)

        for colname in ['high', 'low', 'open', 'close',
                        'change', 'vol', 'amount']:
            # normalize values: (x - x_min)/(x_max - x_min)
            feat['max_{}_win_{}'.format(colname, win)] = self.__norm_val(np.nanmax(df_sub[colname].values),
                                                                         vals_norm, colname)
            feat['min_{}_win_{}'.format(colname, win)] = self.__norm_val(np.nanmin(df_sub[colname].values),
                                                                         vals_norm, colname)
            feat['mean_{}_win_{}'.format(colname, win)] = self.__norm_val(np.nanmean(df_sub[colname].values),
                                                                          vals_norm, colname)
            feat['median_{}_win_{}'.format(colname, win)] = self.__norm_val(np.nanmedian(df_sub[colname].values),
                                                                            vals_norm, colname)
            feat['std_{}_win_{}'.format(colname, win)] = np.nanstd(df_sub[colname].values)

        #  use all values in last 10 days
        if win == 10:
            for d in range(win):
                feat['d{}_{}'.format(d + 1, 'pct_chg')] = df_sub.iloc[d]['pct_chg']
                for colname in ['high', 'low', 'open', 'close',
                                'change', 'vol', 'amount']:
                    feat['d{}_{}'.format(d+1, colname)] = self.__norm_val(df_sub.iloc[d][colname],
                                                                          vals_norm, colname)
        return feat

    def feat_stat_with_win(self, trade_date):
        feat = dict()
        feat.update(self.__abs_feat_stat_last_n_days(trade_date, 5))
        feat.update(self.__abs_feat_stat_last_n_days(trade_date, 10))
        feat.update(self.__abs_feat_stat_last_n_days(trade_date, 15))
        feat.update(self.__abs_feat_stat_last_n_days(trade_date, 30))
        feat.update(self.__abs_feat_stat_last_n_days(trade_date, 60))
        feat.update(self.__abs_feat_stat_last_n_days(trade_date, 90))
        feat.update(self.__abs_feat_stat_last_n_days(trade_date, 120))
        feat.update(self.__abs_feat_stat_last_n_days(trade_date, 150))
        feat.update(self.__abs_feat_stat_last_n_days(trade_date, 180))

        return feat

    def get_y(self, trade_date):
        return self.df.loc[self.df['trade_date'] == trade_date].pct_chg.values[0]

    def feat_moneyflow_hsgt_win(self, trade_date, win=5):
        """
        过去win天资金流向
        :param trade_date:
        :param win:
        :return:
        """
        feat = dict()
        df_sub = self._apply_time_window(trade_date, win, True)

        for colname in ['ggt_ss', 'ggt_sz', 'hgt', 'sgt', 'north_money', 'south_money']:
            for d in range(win):
                # todo speed-up
                feat['d{}_{}'.format(d+1, colname)] = df_sub.iloc[d][colname] if df_sub is not None else None
        return feat


if __name__ == "__main__":

    def calc_feat_stock(filename):
        # filename = 'data/raw/daily_0715/daily_300143.SZ_v20200715.csv'

        ls_trade_date = [20200715, 20200714, 20200713, 20200710, 20200709, 20200708,
                         20200707, 20200706, 20200703, 20200702, 20200701, 20200630,
                         20200629, 20200624, 20200623, 20200622, 20200619, 20200618,
                         20200617, 20200616, 20200615, 20200612, 20200611, 20200610,
                         20200609, 20200608, 20200605, 20200604, 20200603, 20200602,
                         20200601, 20200529, 20200528, 20200527, 20200526, 20200525,
                         20200522, 20200521, 20200520, 20200519, 20200518, 20200515,
                         20200514, 20200513, 20200512, 20200511, 20200508, 20200507,
                         20200506, 20200430, 20200429, 20200428, 20200427, 20200424,
                         20200423, 20200422, 20200421, 20200420, 20200417, 20200416,
                         20200415, 20200414, 20200413, 20200410, 20200409, 20200408,
                         20200407, 20200403, 20200402, 20200401, 20200331, 20200330,
                         20200327, 20200326, 20200325, 20200324, 20200323, 20200320,
                         20200319, 20200318, 20200317, 20200316, 20200313, 20200312,
                         20200311, 20200310, 20200309, 20200306, 20200305, 20200304,
                         20200303, 20200302, 20200228, 20200227, 20200226, 20200225,
                         20200224, 20200221, 20200220, 20200219, 20200218, 20200217,
                         20200214, 20200213, 20200212, 20200211, 20200210, 20200207,
                         20200206, 20200205, 20200204, 20200203, 20200123, 20200122,
                         20200121, 20200120, 20200117, 20200116, 20200115, 20200114,
                         20200113, 20200110, 20200109, 20200108, 20200107, 20200106,
                         20200103, 20200102, 20191231, 20191230, 20191227, 20191226,
                         20191225, 20191224, 20191223, 20191220, 20191219, 20191218,
                         20191217, 20191216, 20191213, 20191212, 20191211, 20191210,
                         20191209, 20191206, 20191205, 20191204, 20191203, 20191202,
                         20191129, 20191128, 20191127, 20191126, 20191125, 20191122,
                         20191121, 20191120, 20191119, 20191118, 20191115, 20191114,
                         20191113, 20191112, 20191111, 20191108, 20191107, 20191106,
                         20191105, 20191104, 20191101, 20191031, 20191030, 20191029,
                         20191028, 20191025, 20191024, 20191023, 20191022, 20191021,
                         20191018, 20191017, 20191016, 20191015, 20191014, 20191011,
                         20191010, 20191009, 20191008, 20190930, 20190927, 20190926,
                         20190925, 20190924, 20190923, 20190920, 20190919, 20190918,
                         20190917, 20190916, 20190912, 20190911, 20190910, 20190909,
                         20190906, 20190905, 20190904, 20190903, 20190902, 20190830,
                         20190829, 20190828, 20190827, 20190826, 20190823, 20190822,
                         20190821, 20190820, 20190819, 20190816, 20190815, 20190814,
                         20190813, 20190812, 20190809, 20190808, 20190807, 20190806,
                         20190805, 20190802, 20190801, 20190731, 20190730, 20190729]
        FB = FeatBasic(filename=filename)

        df_feat = None
        for trade_date in ls_trade_date:
            runid = '{}_{}'.format(filename.split('_')[2], trade_date)

            rlt = FB.feat_moneyflow_hsgt_win(trade_date=trade_date)
            rlt.update(FB.feat_stat_with_win(trade_date=trade_date))

            y = FB.get_y(trade_date)
            print(runid)
            # print(rlt)
            if df_feat is None:
                df_feat = pd.DataFrame(columns=['runid', 'y'] + list(rlt.keys()))
                df_feat.loc[len(df_feat)] = [runid, y] + list(rlt.values())
            else:
                df_feat.loc[len(df_feat)] = [runid, y] + list(rlt.values())

        print(df_feat.head())

        return df_feat

    filenames = glob('data/raw/daily_0715/daily_*.csv')
    print('length of filenames ', len(filenames))

    # r = calc_feat_stock(filenames[0])  # todo test for one stock
    # print(r)
    # r.to_csv('tmp_test_feat.csv')

    for filename in filenames:
        print(filename)
        try:
            df_feat = calc_feat_stock(filename)

            df_feat.to_csv('data/processed/feat_0718/{}'.format(df_feat.runid.iloc[0].split('_')[0]),
                           index=None, encoding='utf-8')
        except:
            # 数据不够的不要了
            pass


