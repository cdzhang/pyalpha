from abc import ABCMeta, abstractmethod
from functools import wraps
import logging
import traceback
import time
from PyUtils.common import lazy_property
from collections import defaultdict


class AbstractTradingStrategy:
    """
    Todo 抽象基类设计, 方便后续回测、比较等
    """

    __metaclass__ = ABCMeta

    def __init__(self, candidate_pool):
        self.candidate_pool = candidate_pool
        self.share = defaultdict()
        self.position = defaultdict(list)
