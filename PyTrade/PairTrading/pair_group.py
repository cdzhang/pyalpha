from PyTrade.abstract_trading_strategy import *
from PyData.data import Stock
from scipy.stats import kendalltau
import pandas as pd
import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import numpy as np
from statsmodels.distributions.empirical_distribution import ECDF
import sys
import scipy.integrate as integrate
from scipy.optimize import least_squares
from copulas import EPSILON

MIN_FLOAT_LOG = np.log(sys.float_info.min)
MAX_FLOAT_LOG = np.log(sys.float_info.max)


class PairTradingGroup(AbstractTradingStrategy):
    def __init__(self, candidate_pool, date_range):
        super().__init__(candidate_pool)
        self.date_range = date_range
        self.trade_now = False

    @lazy_property
    def get_close_price_dict(self):
        """return dict {code : return df with date as index}"""
        rlt = {}

        for i in self.candidate_pool:
            candidate = Stock(i, start=self.date_range[0], end=self.date_range[1])
            df_hist = candidate.df_get_hist[['date', 'close']].set_index('date')
            rlt[i] = df_hist.rename(columns={'close': i})

        return rlt

    @lazy_property
    def get_close_df(self):
        """return df """
        df_list = []
        for i, k in self.get_close_price_dict.items():
            df_list.append(k)

        df_close = pd.concat(df_list, axis=1, sort=True)
        df_close.dropna(axis=0, inplace=True)

        return df_close

    @lazy_property
    def get_log_return_dict(self):
        """return dict {code : return df with date as index}"""
        rlt = {}

        for i in self.candidate_pool:
            candidate = Stock(i, start=self.date_range[0], end=self.date_range[1])
            df_hist = candidate.df_get_hist[['date', 'log_return']].set_index('date')
            rlt[i] = df_hist.rename(columns={'log_return': i})

        return rlt

    @lazy_property
    def get_log_return_df(self):
        """return df """
        df_list = []
        for i, k in self.get_log_return_dict.items():
            df_list.append(k)

        df_logreturn = pd.concat(df_list, axis=1, sort=True)
        df_logreturn.dropna(axis=0, inplace=True)

        return df_logreturn

    @lazy_property
    def get_correlation(self, corr_method='kendall'):
        df_list = []
        for i, k in self.get_log_return_dict.items():
            df_list.append(k)
        df_logreturn = pd.concat(df_list, axis=1, sort=True)
        df_logreturn.dropna(axis=0, inplace=True)
        # df_return = pd.DataFrame(self.get_log_return_dict)
        return df_logreturn.corr(corr_method)

    def test_correlation(self, pair_candidate, window_length=30):
        """test pair correlation manually"""
        if len(pair_candidate) != 2:
            logging.warning(f"illegal pair_candidate {pair_candidate} return None")
            return None

        log_dict = self.get_log_return_dict

        # get log return list
        c1 = log_dict[pair_candidate[0]]
        c2 = log_dict[pair_candidate[1]]

        if len(c1) < window_length:
            logging.warning(f"test window_length longer than stock class date range {window_length} return None")
            return None

        corr, p_value = kendalltau(x=c1[:window_length], y=c2[:window_length])

        logging.info(f"{pair_candidate} correlation {corr} p_value {p_value} ")

        return corr, p_value

    def plot_log_return(self, pair_candidate):

        log_dict = self.get_log_return_df[pair_candidate]

        # get log return list
        c1 = log_dict[pair_candidate[0]]
        c2 = log_dict[pair_candidate[1]]

        tra_date = self.share['tra_date']

        fig = go.Figure()

        trace1 = go.Scatter(x=tra_date, y=c1,
                            name=pair_candidate[0],
                            xaxis='x2', yaxis='y2')
        trace2 = go.Scatter(x=tra_date, y=c2,
                            name=pair_candidate[1],
                            xaxis='x2', yaxis='y2')

        trace3 = go.Scatter(x=tra_date, y=[i - j for i, j in zip(c1, c2)],
                            name='log return spread',
                            xaxis='x2', yaxis='y2')

        fig.add_traces([trace1, trace2, trace3])

        fig.show()

    @staticmethod
    def get_copula_parameter(tau, family='clayton'):

        def _tau_to_theta(alpha):
            """Relationship between tau and theta as a solvable equation."""

            def debye(t):
                return t / (np.exp(t) - 1)

            debye_value = integrate.quad(debye, EPSILON, alpha)[0] / alpha
            return 4 * (debye_value - 1) / alpha + 1 - tau

        if family == 'clayton':
            return 2 * tau / (1 - tau)
        elif family == 'frank':
            result = least_squares(_tau_to_theta, 1, bounds=(MIN_FLOAT_LOG, MAX_FLOAT_LOG))
            return result.x[0]
        else:
            """gumbel"""
            return 1 / (1 - tau)

    def _train_copula(self, log_return_a, log_return_b, family):

        self.ecdf_a, self.ecdf_b = ECDF(log_return_a), ECDF(log_return_b)

        tau, _ = kendalltau(x=log_return_a, y=log_return_b)

        self.param = self.get_copula_parameter(tau, family=family)

    def _mispricing_index(self, x, y, family):
        """calculate MI_(x|y) MI_(x|y)"""
        u, v = self.ecdf_a(x), self.ecdf_b(y)

        theta = self.param

        if u == 0 and v == 0:
            u, v = 0.0001, 0.0001

        if family == 'clayton':
            mi_vonu = math.pow(u, - theta - 1) * math.pow(math.pow(u, - theta) + math.pow(v, - theta) - 1,
                                                          - math.pow(theta, -1) - 1)

            mi_uonv = math.pow(v, - theta - 1) * math.pow(math.pow(u, - theta) + math.pow(v, - theta) - 1,
                                                          - math.pow(theta, -1) - 1)
        else:
            # frank
            mi_vonu = ((math.exp(- theta * u) - 1) * (math.exp(- theta * v) - 1) + (math.exp(- theta * v) - 1)) / (
                        (math.exp(- theta * u) - 1) * (math.exp(- theta * v) - 1) + (math.exp(- theta) - 1))

            mi_uonv = ((math.exp(- theta * u) - 1) * (math.exp(- theta * v) - 1) + (math.exp(- theta * u) - 1)) / (
                    (math.exp(- theta * u) - 1) * (math.exp(- theta * v) - 1) + (math.exp(- theta) - 1))

        return mi_uonv, mi_vonu

    # def generate_position_list(self, mi_uonv, mi_vonu):
    #     if mi_uonv <= 0.05:
    #         self.trade_now = True
    #         self.position['u'].append(1)
    #         self.position['v'].append(0)
    #     elif mi_vonu <= 0.05:
    #         self.trade_now = True
    #         self.position['u'].append(0)
    #         self.position['v'].append(1)
    #     else:
    #         self.trade_now = False
    #         self.position['u'].append(self.position['u'][-1])
    #         self.position['v'].append(self.position['v'][-1])

    def trade_signal(self, pair_candidate, train_length, family, if_viz=True):

        self.position['u'] = [0] * train_length
        self.position['v'] = [0] * train_length

        # 1st train copula
        log_df = self.get_log_return_df[pair_candidate]

        a = log_df[pair_candidate[0]]
        b = log_df[pair_candidate[1]]

        self._train_copula(log_return_a=a[:train_length], log_return_b=b[:train_length], family=family)

        i = 0
        test_period = log_df.index[train_length:]
        mi_uonv_ls = []
        mi_vonu_ls = []
        while i < len(a) - train_length:
            traday_index = train_length + i
            mi_uonv, mi_vonu = self._mispricing_index(x=a[traday_index], y=b[traday_index], family=family)
            mi_uonv_ls.append(mi_uonv)
            mi_vonu_ls.append(mi_vonu)
            i += 1
            # self.generate_position_list(mi_uonv, mi_vonu)
        rlt = pd.DataFrame(columns=['date', 'mi_uonv', 'mi_vonu'])
        rlt = rlt.assign(date=test_period, mi_uonv=mi_uonv_ls, mi_vonu=mi_vonu_ls)

        # print(rlt.head(6))
        # TODO optimize trading threshold
        u_signal = [pd.to_datetime(i).date() for i in rlt[rlt.mi_uonv < 0.05].date]
        # v_signal = rlt[rlt.mi_vonu < 0.05].date
        u_sell = [pd.to_datetime(i).date() for i in rlt[rlt.mi_uonv > 0.9].date]

        # rlt = []
        #
        # for buy in u_signal:
        #     rlt.append({'date': buy, 'action': 'buy'})
        #
        # i = 0
        # i_sell = 0
        # while i < len(u_sell) + len(u_signal):
        #     if rlt[i]['date'] < u_sell[i] and rlt[i]['action'] == 'buy':
        #         rlt.append({'date': u_sell[i], 'action': 'sell'})
        #         i += 1



        if if_viz:
            df_close_u = self.get_close_df[pair_candidate[0]][train_length:]
            df_close_v = self.get_close_df[pair_candidate[1]][train_length:]

            fig = make_subplots(specs=[[{"secondary_y": True}]])

            trace1 = go.Scatter(y=df_close_u, x=df_close_u.index,
                                name=pair_candidate[0],
                                xaxis='x2', yaxis='y2')

            fig.add_trace(trace1, secondary_y=False)

            for i in u_signal:
                trace_tmp = go.Scatter(y=[0, 1], x=[pd.to_datetime(i).date(), pd.to_datetime(i).date()],
                                       name="mispricing index: buy",
                                       xaxis='x2', yaxis='y2', mode="lines",
                                       line_color="tomato"
                                       )
                fig.add_trace(trace_tmp, secondary_y=True)

            for i in u_sell:
                trace_tmp = go.Scatter(y=[0, 1], x=[pd.to_datetime(i).date(), pd.to_datetime(i).date()],
                                       name="mispricing index: sell",
                                       xaxis='x2', yaxis='y2', mode="lines",
                                       line_color="peachpuff"
                                       )
                fig.add_trace(trace_tmp, secondary_y=True)

            fig.show()
        return rlt, u_signal, u_sell, df_close_u, df_close_v









