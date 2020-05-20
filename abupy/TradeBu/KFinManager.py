#-*-coding:utf-8-*-
"""
    财务数据管理模块
"""

__author__ = 'K'

from ..MarketBu.KSymbolFin import FinDataSource
from abupy.UtilBu import ABuRegUtil
import numpy as np

class KFinManager(object):
    def __init__(self):
        self.ds = FinDataSource()
        self.fin_cache = {}

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

    def get_finindicator_flat(self,start,end):
        fin = self.get_finindicator(start,end)

        def _value_worth(df):
            dic = {}
            roe_dt_year = df.loc[df.end_date.contains['1231']]
            for i in range(2, 5):
                dic['roe_dt_' + i] = np.where(i >= roe_dt_year.sharp[0], roe_dt_year.roe_dt[0:i].mean(), np.nan)
                dic['roe_dt_deg' + i] = np.where(i >= roe_dt_year.sharp[0], ABuRegUtil.calc_regress_deg(roe_dt_year.roe_dt[0:i]), np.nan)
                # 销售毛利率
                dic['grossprofit_margin' + i] = np.where(i >= roe_dt_year.sharp[0], roe_dt_year.grossprofit_margin[0:i].mean(), np.nan)
                dic['grossprofit_margin_deg' + i] = np.where(i >= roe_dt_year.sharp[0], ABuRegUtil.calc_regress_deg(roe_dt_year.grossprofit_margin[0:i]), np.nan)
                # 扣非净利润
                dic['profit_dedt' + i] = np.where(i >= roe_dt_year.sharp[0], roe_dt_year.profit_dedt[0:i].mean(), np.nan)
                dic['profit_dedt_deg' + i] = np.where(i >= roe_dt_year.sharp[0], ABuRegUtil.calc_regress_deg(roe_dt_year.profit_dedt[0:i]), np.nan)
                # 营业利润同比增长
                dic['op_yoy_' + i] = np.where(i >= roe_dt_year.sharp[0], roe_dt_year.op_yoy[0:i].mean(), np.nan)

            end_date = df.iloc[0].end_date
            dic['roe_dt_year'] = df.iloc[0].roe_dt * 12 / int(end_date[4:5])
            dic['end_date'] = end_date
            dic['ann_code'] = df.iloc[0].ann_date
            dic['ts_code'] = df.iloc[0].ts_code
            return dic
        return fin.groupby('ts_code').apply(_value_worth)