import pymysql

# Connect to the database
# connection = pymysql.connect(host='host',
#                              user='root',
#                              password='maoxiaomi123',
#                              db='alpha',
#                              charset='utf8mb4',
#                              cursorclass=pymysql.cursors.DictCursor)

# connection = pymysql.connect(db='alpha',
#                              user='root',
#                              passwd='maoxiaomi123',
#                              host='localhost',
#                              port=8084)
# todo always close connection: connection.close()

def test():
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `stock_daily` (`ts_code`, `trade_date`, `open`, `high`, `low`, `close`, " \
                  "`pre_close`, `change`, `pct_chg`, `vol`, `amount`) VALUES (%s, %s, %s, %s, %s, %s, " \
                  "%s, %s, %s, %s, %s)"
            cursor.execute(sql, ('000728.SZ', '20200716', 10.75, 11.08, 10.33, 10.39,
                                 10.81, -0.42, -3.8853, 837829.11, 898536.174))
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

        # with connection.cursor() as cursor:
        #     # Read a single record
        #     sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
        #     cursor.execute(sql, ('webmaster@python.org',))
        #     result = cursor.fetchone()
        #     print(result)
    finally:
        connection.close()


def write_stock_daily(df):
    """

    :param df: daily stock dataframe from tushare
    :return:
    """
    for i in range(len(df)):
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `daily` (`ts_code`, `trade_date`, `open`, `high`, `low`, `close`, " \
                      "`pre_close`, `change`, `pct_chg`, `vol`, `amount`) VALUES ('{}', '{}', {}, {}, {}, {}, " \
                      "{}, {}, {}, {}, {})".format(df.iloc[i].values[0],
                                                   df.iloc[i].values[1],
                                                   df.iloc[i].values[2],
                                                   df.iloc[i].values[3],
                                                   df.iloc[i].values[4],
                                                   df.iloc[i].values[5],
                                                   df.iloc[i].values[6],
                                                   df.iloc[i].values[7],
                                                   df.iloc[i].values[8],
                                                   df.iloc[i].values[9],
                                                   df.iloc[i].values[10],
                                                   )
                cursor.execute(sql)
            # commit it
            connection.commit()
        except Exception as err:
            print('error inserting ', err)

    return None


def save_local2daily():
    from glob import glob
    filenames = glob('/Users/dan/daynity/pyalpha-data/raw/daily_0715/daily*v20200715.csv')

    for filename in filenames:
        df = pd.read_csv(filename)
        df = df[['ts_code', 'trade_date', 'open', 'high', 'low', 'close',
                 'pre_close', 'change', 'pct_chg', 'vol', 'amount']]
        print('len of {}: {}'.format(filename, len(df)))
        write_stock_daily(df)

    connection.close()


if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    import tushare as ts
    import json

    with open('PyData/hist_data/stock_basic.json') as json_file:
        data = json.load(json_file)

    # print(data.keys())



    ts.set_token('7dd7dc496ee9de8e4c8052e54ec22ac23f8f1ad8b05aa42603a1e472')
    pro = ts.pro_api()
    for ts_code in list(data.keys())[2501:]:
        df = pro.daily(ts_code=ts_code, start_date='20050101', end_date='20200728')
        df = df[['ts_code', 'trade_date', 'open', 'high', 'low', 'close',
                 'pre_close', 'change', 'pct_chg', 'vol', 'amount']]
        print('len of {}: {}'.format(ts_code, len(df)))
        # write_stock_daily(df)

        df.to_csv('/Users/dan/daynity/pyalpha-data/raw/daily_0728/daily_{}_0728.csv'.format(ts_code), encoding='utf-8', index=None)

    # connection.close()