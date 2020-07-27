# -*- coding: UTF-8 -*-

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from glob import glob
import matplotlib.pyplot as plt

# from statsmodels.tsa.stattools import coint # todo warning do not use it
from statsmodels.tsa.stattools import adfuller


def read_2_df(filename1, filename2):
    df1 = pd.read_csv(filename1)
    df2 = pd.read_csv(filename2)

    # merge 2 dataframes
    if 'trade_date' in df1.columns:
        df1 = df1.sort_values(by=['trade_date'], ascending=True)
        df2 = df2.sort_values(by=['trade_date'], ascending=True)
        df = pd.merge(df1, df2, on=['trade_date'], how='inner')
        df1 = pd.merge(df[['trade_date']], df1, on=['trade_date'], how='inner')
        df2 = pd.merge(df[['trade_date']], df2, on=['trade_date'], how='inner')
    else:
        df1 = df1.sort_values(by=['date'], ascending=True)
        df2 = df2.sort_values(by=['date'], ascending=True)
        df = pd.merge(df1, df2, on=['date'], how='inner')
        df1 = pd.merge(df[['date']], df1, on=['trade_date'], how='inner')
        df2 = pd.merge(df[['date']], df2, on=['trade_date'], how='inner')


    return df1, df2


def get_2_filenames(A_name, B_name):
    filenames = glob('data/raw/daily*')

    for filename in filenames:
        if A_name in filename:
            filename1 = filename
        if B_name in filename:
            filename2 = filename
    return filename1, filename2


def plot_2_lines(filename1, filename2):
    """

    :param filename1: 'data/daily_西部证券_002673.SZ.csv'
    :param filename2: 'data/daily_长城证券_002939.SZ.csv'
    :return:
    """
    df1, df2 = read_2_df(filename1, filename2)

    x = [k for k in range(len(df1))]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=df1.close,
        name = filename1,
        connectgaps=True
    ))

    fig.add_trace(go.Scatter(
        x=x,
        y=df2.close,
        name=filename2,
    ))

    fig.show()
    return None


# 设置开仓和止损的阈值
def plot_sigma(filename1, filename2):
    df1, df2 = read_2_df(filename1, filename2)
    price_A = df1.close.values
    price_B = df2.close.values

    spread = price_A - price_B
    mspread = spread - np.mean(spread)
    sigma = np.std(mspread)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(range(len(mspread)), mspread)

    ax.hlines(0, 0, len(mspread))
    ax.hlines(2 * sigma, 0, len(mspread), colors='b')
    ax.hlines(-2 * sigma, 0, len(mspread), colors='b')
    ax.hlines(3 * sigma, 0, len(mspread), colors='r')
    ax.hlines(-3 * sigma, 0, len(mspread), colors='r')
    fig.show()
    return None


def check_coint(filename1, filename2, p_value_set = 0.05, crit_value_bar=5):
    """
    # 协整检验
    :param filename1:
    :param filename2:
    :param p_value_set:
    :param crit_value_bar: int, in [1, 5, 10]
    :return:
    """
    df1, df2 = read_2_df(filename1, filename2)
    price_A = df1.close.values
    price_B = df2.close.values

    a3 = price_A - price_B
    rlt = adfuller(a3)  # 使用adf单位根检验平稳性
    print(rlt)

    # rlt = coint(price_A, price_B) # todo do not use it

    t = rlt[0]
    p = rlt[1]
    crit_value_1 = rlt[4].get('1%')
    crit_value_5 = rlt[4].get('5%')
    crit_value_10 = rlt[4].get('10%')

    if p <= p_value_set:
        # compare t with crit_values
        if crit_value_bar == 1:
            if t < crit_value_1:
                return [t, p, crit_value_1, crit_value_5, crit_value_10, True]
        elif crit_value_bar == 5:
            if t < crit_value_5:
                return [t, p, crit_value_1, crit_value_5, crit_value_10, True]
        else:
            if t < crit_value_10:
                return [t, p, crit_value_1, crit_value_5, crit_value_10, True]
    return [t, p, crit_value_1, crit_value_5, crit_value_10, False]


if __name__ == '__main__':
    from glob import glob
    filenames = glob('data/raw/daily*.csv')
    print('len of all stocks ', len(filenames))

    df_rlt = pd.DataFrame(columns=['A_name', 'A_code', 'B_name', 'B_code', 't', 'p',
                                     'crit_value_1',
                                     'crit_value_5',
                                     'crit_value_10', 'flag'])

    # filename1 = 'data/raw/daily_光大证券_601788.SH.csv'
    # filename2 = 'data/raw/daily_中信建投_601066.SH.csv'
    #
    # print(check_coint(filename1, filename2))
    # print(check_coint(filename2, filename1))

    for f1 in filenames:
        for f2 in filenames:
            if f1 != f2:
                print(f1, f2)
                rlt = check_coint(f1, f2)
                print(rlt, '\n')
                A_name, A_code = f1.split('_')[1], f1.split('_')[2].replace('.csv', '')
                B_name, B_code = f2.split('_')[1], f2.split('_')[2].replace('.csv', '')
                df_rlt.loc[len(df_rlt)] = [A_name, A_code,
                                           B_name, B_code,
                                           rlt[0],
                                           rlt[1],
                                           rlt[2],
                                           rlt[3],
                                           rlt[4],
                                           rlt[5]
                                           ]

    df_rlt.to_csv('data/processed/check_coint_20200717.csv', encoding='utf-8')


