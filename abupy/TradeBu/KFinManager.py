#-*-coding:utf-8-*-
"""
    财务数据管理模块
"""

__author__ = 'K'

from ..MarketBu.KSymbolFin import FinDataSource

class KFinManager(object):
    def __init__(self):
        self.ds = FinDataSource()

    def get_stock_daily_basic(self, start, end, code=None):
        return self.ds.get_stock_daily_basic(start,end,code)

    def get_assetAliability(self, start, end, code=None):
        return self.ds.get_assetAliability(start, end, code)

    def get_cashflow(self, start, end, code=None):
        return self.ds.get_cashflow(start, end, code)

    def get_income(self, start, end, code=None):
        return self.ds.get_income(start, end, code)

    def get_daily_adj(self, start, end, code=None):
        return self.ds.get_daily_adj(start, end, code)

    def get_money_flow(self, start, end, code=None):
        return self.ds.get_money_flow(start, end, code)

    def get_finindicator(self, start, end, code=None):
        return self.ds.get_finindicator(start, end, code)