from abc import ABCMeta, abstractmethod
from functools import wraps
import logging
import traceback
import time


class AbstractTradingStrategy:
    """
    Todo 抽象基类设计, 方便后续回测、比较等
    """

    __metaclass__ = ABCMeta

    def __init__(self, candidate_pool, signal_pool):
        self.candidate_pool = candidate_pool
        self.signal_pool = signal_pool

    @abstractmethod
    def calc_return(self, start, end):
        """统一接口"""
        pass
