#-*-coding:utf-8-*-
from .ABuPickStockBase import AbuPickStockBase

__author__ = 'k'

class KPickStockValue(AbuPickStockBase):
    def _init_self(self, **kwargs):
        """通过kwargs设置位移路程比选股条件，配置因子参数"""
        self.profit = kwargs.pop('profit', None)
        self.asset = kwargs.pop('asset', None)
        self.basic = kwargs.pop('basic', None)

    def fit_pick(self, kl_pd, target_symbol):
        pass

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        ast = pick_worker.fin_manager.get_assetAliability()
        basic  = pick_worker.fin_manager.get_stock_daily_basic()
        fin = pick_worker.fin_manager.get_finindicator()
        basic[(fin.grossprofit_margin>30) &]
        #income = get_income
        pass
