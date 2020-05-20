#-*-coding:utf-8-*-
from abupy.UtilBu import ABuRegUtil
from .ABuPickStockBase import AbuPickStockBase
import numpy as np

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
        """ 毛利率大于 35 且近两年roe >15 ，且现金流匹配度要"""
        ast = pick_worker.fin_manager.get_assetAliability()
        basic  = pick_worker.fin_manager.get_stock_daily_basic()
        fin = pick_worker.fin_manager.get_finindicator_flat()
        return fin[(fin.roe_dt_2>15) & (fin.grossprofit_margin>35)].ts_code.values.tolist()
        pass
