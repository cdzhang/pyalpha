import tushare as ts 
ts.set_token('7dd7dc496ee9de8e4c8052e54ec22ac23f8f1ad8b05aa42603a1e472')
pro = ts.pro_api()
df = pro.daily(ts_code='000001.SZ', start_date='20180701', end_date='20200715')

