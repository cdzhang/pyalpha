import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve


def hp_filter(X, lamb=100):
    """
    Hodrick-Prescott Filter
    ref: https://www.quantconnect.com/tutorials/strategy-library/the-momentum-strategy-based-on-the-low-frequency-component-of-forex-market
    :param X: input time series
    :param lamb:
    :return:
    """
    X = np.asarray(X, float)
    if X.ndim > 1:
        X = X.squeeze()

    nobs = len(X)
    I = sparse.eye(nobs,nobs)
    offsets = np.array([0,1,2])
    # 双侧HP滤波
    # they are by construction a function of future realizations
    data = np.repeat([[1.],[-2.],[1.]], nobs, axis=1)
    K = sparse.dia_matrix((data, offsets), shape=(nobs-2, nobs))
    use_umfpack = True
    trend = spsolve(I+lamb*K.T.dot(K), X, use_umfpack=use_umfpack)
    cycle = X - trend
    return trend, cycle


def kalman_filter(X):
    # TODO
    return None
