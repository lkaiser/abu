#-*-coding:utf-8-*-
from .ABuPickStockBase import AbuPickStockBase, reversed_result

__author__ = 'K'

class KPickStockValue(AbuPickStockBase):
    """白马选择指标，选取毛利率>35% 且近两年平均 roe> 15%的个股，且近2毛利率趋势至少不下降吧，近3年现金流利润比不能低于70%"""
    def _init_self(self, **kwargs):
        """通过kwargs设置位条件，配置因子参数"""
        self.start = kwargs['start']
        self.end = kwargs['end']
        self.roe_dt_2 = kwargs['roe_dt_2']
        self.grossprofit_margin = kwargs['grossprofit_margin'] if 'grossprofit_margin' in kwargs else None
        self.ocf_to_opincome = kwargs['ocf_to_opincome'] if 'ocf_to_opincome' in kwargs else None


    def fit_pick(self, kl_pd, target_symbol):
        """精挑"""
        return True

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        """普选 毛利率大于 35 且近两年roe >15 ，且现金流、营业利润匹配度要合理，比如近2年>0.8 近3年>0.7"""
        #ast = pick_worker.fin_manager.get_assetAliability()
        #basic  = pick_worker.fin_manager.get_stock_daily_basic()
        fin = pick_worker.fin_manager.get_finindicator_flat(self.start,self.end)

        fin = fin[(fin.roe_dt_2 > self.roe_dt_2)]
        if self.grossprofit_margin is not None:
            fin = fin[(fin.grossprofit_margin > self.grossprofit_margin)]
        if self.ocf_to_opincome is not None:
            fin = fin[(fin.ocf_to_opincome_2 > self.ocf_to_opincome) | (fin.ocf_to_opincome_3 > self.ocf_to_opincome)]
        #根据输入choice_symbols 取交集
        return list(set(fin.index.values).intersection(set(choice_symbols))) if (choice_symbols is not None and len(choice_symbols) > 0) else fin.index.values.list()

