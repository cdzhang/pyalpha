import pandas as pd


def read_hist_csv(file_dir):
    df_hist = pd.read_csv(file_dir, sep=',')
    df_hist['date'] = df_hist['date'].apply(pd.to_datetime)
    df_hist.sort_values('date', ascending=True, inplace=True)
    return df_hist


