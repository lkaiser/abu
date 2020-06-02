#-*-coding:utf-8-*-
from .ABuPickStockBase import AbuPickStockBase, reversed_result

__author__ = 'K'

class KPickStockValue(AbuPickStockBase):
    def _init_self(self, **kwargs):
        """通过kwargs设置位条件，配置因子参数"""
        self.start = kwargs['start']
        self.end = kwargs['end']
        #self.first_choice

    def fit_pick(self, kl_pd, target_symbol):
        """精挑"""
        return True

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        """普选 毛利率大于 35 且近两年roe >15 ，且现金流匹配度要"""
        #ast = pick_worker.fin_manager.get_assetAliability()
        #basic  = pick_worker.fin_manager.get_stock_daily_basic()
        fin = pick_worker.fin_manager.get_finindicator_flat(self.start,self.end)

        fin = fin[(fin.roe_dt_2 > 15) & (fin.grossprofit_margin > 35) &(fin.grossprofit_margin_recent_deg2>0)]
        #根据输入choice_symbols 取交集
        return list(set(fin.index.values).intersection(set(choice_symbols))) if (choice_symbols is not None and len(choice_symbols) > 0) else fin.index.values.list()

