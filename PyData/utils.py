import pandas as pd


def read_hist_csv(file_dir):
    df_hist = pd.read_csv(file_dir, sep=',')
    # different returned columns
    # df_hist.columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close',
    #                    'change', 'pct_chg', 'vol', 'amount'] # new pro version
    # ['date', 'open', 'high', 'close', 'low', 'volume', 'price_change',
    #  'p_change', 'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'] # pre

    df_hist.columns = ['ts_code', 'date', 'open', 'high', 'low', 'close', 'pre_close',
                       'price_change', 'p_change', 'volume', 'amount']
    df_hist['date'] = df_hist['date'].apply(pd.to_datetime, format='%Y%m%d', errors='ignore') # new api
    df_hist.sort_values('date', ascending=True, inplace=True)
    return df_hist



