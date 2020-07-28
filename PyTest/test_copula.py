# from PyData.data import ts_pro, ts, Stock, stock_json
from datetime import datetime
import os
import pandas as pd
import logging
import time
from PyData.config import HIST_DIR
import plotly.figure_factory as ff
import plotly.graph_objects as go
import numpy as np
from PyTrade.PairTrading.pair_group import PairTradingGroup
import json
import math


def test_pair(code_list, if_viz=False):
    #     code_list = [key.split('.')[0] for key, value in stock_json.items() if
    #                  (value['industry'] == '啤酒') and 'ST' not in value['name']]
    # print(code_list)
    x = PairTradingGroup(candidate_pool=code_list, date_range=['2018-07-25', '2020-07-25'])
    # df_correlation = x.get_correlation
    # print(df_correlation)
    # print(x.trade_signal(pair_candidate=['600132', '600600'], train_length=60, family='clayton'))
    # print(df_correlation.max())
    # print(x.test_correlation(pair_candidate=['000858', '000568']))
    # x.plot_log_return(pair_candidate=['600600', '600573'])
    # return df_correlation
    # TODO find best train_length
    # todo find best family
    # todo find best pairs
    return x.trade_signal(pair_candidate=code_list, train_length=180, family='clayton', if_viz=if_viz)


# rlt_u, buy_u, sell_u, df_close_u, df_close_v = test_pair(code_list)
# rlt_v, buy_v, sell_v, _, _ = test_pair([code_list[1], code_list[0]])

def apply_strategy(code_list, df_close_u, df_close_v, buy_u, sell_u, buy_v, sell_v):
    df = pd.merge(pd.DataFrame(df_close_u), pd.DataFrame(df_close_v), left_index=True, right_index=True)
    df = df.assign(date=df.index)
    df = df[['date'] + code_list]

    df.date = [pd.to_datetime(i).date() for i in df.date]
    df.index = list(range(len(df)))

    # signal dataframe
    df_sell_u = pd.DataFrame(columns=['date'], data=sell_u)
    df_sell_u = df_sell_u.assign(sell_u_signal = 1)
    # df_sell_u.index = df_sell_u['date']
    # del df_sell_u['date']

    df_buy_u = pd.DataFrame(columns=['date'], data=buy_u)
    df_buy_u = df_buy_u.assign(buy_u_signal = 1)
    # df_buy_u.index = df_buy_u['date']
    # del df_buy_u['date']

    df_sell_v = pd.DataFrame(columns=['date'], data=sell_v)
    df_sell_v = df_sell_v.assign(sell_v_signal=1)
    # df_sell_v.index = df_sell_v['date']
    # del df_sell_v['date']

    df_buy_v = pd.DataFrame(columns=['date'], data=buy_v)
    df_buy_v = df_buy_v.assign(buy_v_signal=1)
    # df_buy_v.index = df_buy_v['date']
    # del df_buy_v['date']

    df = pd.merge(df, df_sell_u, on=['date'], how='left')
    df = pd.merge(df, df_buy_u, on=['date'], how='left')

    df = pd.merge(df, df_sell_v, on=['date'], how='left')
    df = pd.merge(df, df_buy_v, on=['date'], how='left')
    # df.to_excel('notebooks/output/copula_pair_strategy.xlsx')

    # 存u/v买入的的仓位点
    ls_u_cangwei = []
    ls_v_cangwei = []

    df_rt_u = pd.DataFrame(columns=['date', 'u_in_price', 'u_out_price'])
    df_rt_v = pd.DataFrame(columns=['date', 'v_in_price', 'v_out_price'])

    max_u = 0
    max_v = 0
    max_uv = 0

    for i in range(1, len(df)):
        date_now = df.date.iloc[i]
        sell_u = df.sell_u_signal.iloc[i]
        buy_u = df.buy_u_signal.iloc[i]
        sell_v = df.sell_v_signal.iloc[i]
        buy_v = df.buy_v_signal.iloc[i]

        if sell_u == 1 and len(ls_u_cangwei) == 0:
            pass
        if sell_u == 1 and len(ls_u_cangwei) > 0:
            # gain_u_i = sum(df.loc[(df['date'] <= date_now) & (df['date'] > ls_u_cangwei[0])].log_rt_u)
            # gain_u.append(gain_u_i)
            df_rt_u.loc[len(df_rt_u)] = [date_now,
                                         df.loc[df['date'] == ls_u_cangwei[0]][code_list[0]].values[0],
                                         df[code_list[0]].iloc[i]]
            ls_u_cangwei.pop(0)  # remove left first
        if buy_u == 1:
            ls_u_cangwei.append(date_now)

        if sell_v == 1 and len(ls_v_cangwei) == 0:
            pass
        if sell_v == 1 and len(ls_v_cangwei) > 0:
            # gain_v_i = sum(df.loc[(df['date'] <= date_now) & (df['date'] > ls_v_cangwei[0])].log_rt_v)
            # gain_v.append(gain_v_i)
            df_rt_v.loc[len(df_rt_v)] = [date_now,
                                         df.loc[df['date'] == ls_v_cangwei[0]][code_list[1]].values[0],
                                         df[code_list[1]].iloc[i]]
            ls_v_cangwei.pop(0)  # remove left first
        if buy_v == 1:
            ls_v_cangwei.append(date_now)

        max_u = max(max_u,
                    pd.merge(df, pd.DataFrame(columns=['date'], data=ls_u_cangwei), on=['date'], how='inner')[
                        code_list[0]].sum())
        max_v = max(max_v,
                    pd.merge(df, pd.DataFrame(columns=['date'], data=ls_v_cangwei), on=['date'], how='inner')[
                        code_list[0]].sum())

        max_uv = max(max_uv, max_u + max_v)

    # print(max_u, max_v)
    # print('同时在仓的总和', max_uv)

    return max_uv, df_rt_u, df_rt_v


def cum_return(max_uv, df_rt_u, df_rt_v):
    # 最大回撤
    df_rt_u = df_rt_u.assign(rt_u=df_rt_u.u_out_price - df_rt_u.u_in_price)
    df_rt_u = df_rt_u.assign(cum_rt_u=np.cumsum(df_rt_u.rt_u))

    df_rt_v = df_rt_v.assign(rt_v=df_rt_v.v_out_price - df_rt_v.v_in_price)
    df_rt_v = df_rt_v.assign(cum_rt_v=np.cumsum(df_rt_v.rt_v))
    df_rt = pd.merge(df_rt_u, df_rt_v, on=['date'], how='outer')
    df_rt = df_rt.sort_values(by=['date'], ascending=True)
    df_rt.index = range(len(df_rt))
    rt_uv = [np.nansum([df_rt.rt_u.iloc[k], df_rt.rt_v.iloc[k]]) for k in range(len(df_rt))]
    df_rt = df_rt.assign(rt_uv=rt_uv)
    df_rt = df_rt.assign(cum_rt_uv=np.cumsum(df_rt.rt_uv))
    df_rt.head(2)

    duration = (df_rt_u.date.max() - df_rt_u.date.min()).days / 365
    overall_rt = (np.nansum(df_rt_u.rt_u) + np.nansum(df_rt_v.rt_v)) / max_uv
    annual_rt = math.pow(overall_rt + 1,
                         1 / duration) - 1
    down = min(df_rt.cum_rt_uv)

    print('同时在仓的总和', round(max_uv, 2))

    print('总投资时长 {} 年'.format(round(duration, 2)))
    print('总收益率 {}/{} ={}%'.format(round((np.nansum(df_rt_u.rt_u) + np.nansum(df_rt_v.rt_v)), 2),
                                      max_uv,
                                      round(overall_rt * 100, 2)))
    print('年化收益率{}%'.format(round(annual_rt * 100, 2)))
    print('最大回撤', 0 if down > 0 else round(down / max_uv * 100, 2), '%')

    return df_rt


if __name__ == '__main__':
    # code_list = ['000001', '600000']  # 银行跌了，我没赔钱
    # rlt_u, buy_u, sell_u, df_close_u, df_close_v = test_pair(code_list)
    # rlt_v, buy_v, sell_v, _, _ = test_pair([code_list[1], code_list[0]])

    # max_uv, df_rt_u, df_rt_v = apply_strategy(code_list, df_close_u, df_close_v, buy_u, sell_u, buy_v, sell_v)
    # df_rt = cum_return(max_uv, df_rt_u, df_rt_v)

    short_list = ['000001.SZ', '002142.SZ', '002807.SZ', '002839.SZ', '002936.SZ',
                  '002948.SZ', '002958.SZ', '002966.SZ', '600000.SH', '600015.SH',
                  '600016.SH', '600036.SH', '600908.SH', '600919.SH', '600926.SH',
                  '600928.SH', '601009.SH', '601077.SH', '601128.SH', '601166.SH',
                  '601169.SH', '601229.SH', '601288.SH', '601328.SH', '601398.SH',
                  '601577.SH', '601658.SH', '601818.SH', '601838.SH', '601860.SH',
                  '601916.SH', '601939.SH', '601988.SH', '601997.SH', '601998.SH',
                  '603323.SH']

    for u_code in ['600000.SH']:
        for v_code in short_list:
            if u_code != v_code:
                code_list = [u_code.split('.')[0], v_code.split('.')[0]]
                print(code_list)
                rlt_u, buy_u, sell_u, df_close_u, df_close_v = test_pair(code_list)
                rlt_v, buy_v, sell_v, _, _ = test_pair([code_list[1], code_list[0]])

                max_uv, df_rt_u, df_rt_v = apply_strategy(code_list, df_close_u, df_close_v, buy_u, sell_u, buy_v,
                                                          sell_v)
                df_rt = cum_return(max_uv, df_rt_u, df_rt_v)
                # except:
                    # pass
                print('-' * 100)

