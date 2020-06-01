#-*-coding:utf-8-*-
"""
    财务数据管理模块
"""

__author__ = 'K'

from ..MarketBu.KSymbolFin import FinDataSource
from abupy.UtilBu import ABuRegUtil
import numpy as np
import pandas as pd
import math

class KFinManager(object):
    def __init__(self):
        self.ds = FinDataSource()
        self.fin_cache = {}

    def get_stock_daily(self, start, end, code=None):
        return self.ds.get_stock_daily(start,end,code)

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
        fin = self.get_finindicator(start,end).sort_values(['ts_code', 'end_date'], ascending=False)

        def _value_worth(df):
            #涉及到deg的数据都要归一化处理
            dic = {}
            roe_dt_year = df.loc[df.end_date.str.contains('1231')]
            for i in range(2, 5):
                dic['roe_dt_%d' % i] = np.where(i <= roe_dt_year.shape[0], round(roe_dt_year.roe_dt[0:i].mean(),4), np.nan)
                dic['roe_dt_deg%d' % i] = np.where(i <= roe_dt_year.shape[0], round(ABuRegUtil.calc_regress_deg(roe_dt_year.roe_dt[0:i][::-1],show=False),4), np.nan)
                # 销售毛利率
                dic['grossprofit_margin%d' % i] = np.where(i <= roe_dt_year.shape[0], round(roe_dt_year.grossprofit_margin[0:i].mean(),4), np.nan)
                dic['grossprofit_margin_deg%d' % i] = np.where(i <= roe_dt_year.shape[0], round(ABuRegUtil.calc_regress_deg(roe_dt_year.grossprofit_margin[0:i][::-1],show=False),4), np.nan)
                # 扣非净利润
                dic['profit_dedt%d' % i] = np.where(i <= roe_dt_year.shape[0], round(roe_dt_year.profit_dedt[0:i].mean(),4), np.nan)
                dic['profit_dedt_deg%d' % i] = np.where(i <= roe_dt_year.shape[0], round(ABuRegUtil.calc_regress_deg(roe_dt_year.profit_dedt[0:i][::-1],show=False),4), np.nan)
                # 营业利润同比增长
                dic['op_yoy_%d' % i] = np.where(i <= roe_dt_year.shape[0], round(roe_dt_year.op_yoy[0:i].mean(),4), np.nan)
                # 经营现金流/经营净收益比值及变动趋势
                dic['ocf_to_opincome%d' % i] = np.where(i <= roe_dt_year.shape[0], round(roe_dt_year.ocf_to_opincome[0:i].mean(),4), np.nan)
                dic['ocf_to_opincome_deg%d' % i] = np.where(i <= roe_dt_year.shape[0], round(ABuRegUtil.calc_regress_deg(roe_dt_year.ocf_to_opincome[0:i][::-1],show=False),4), np.nan)



            end_date = df.iloc[0].end_date
            dic['roe_dt_year'] = np.nan if math.isnan(df.iloc[0].roe_dt) else int(df.iloc[0].roe_dt) * 12 / int(end_date[4:6])
            dic['end_date'] = end_date
            dic['ann_code'] = df.iloc[0].ann_date
            dic['grossprofit_margin'] = df.iloc[0].grossprofit_margin
            dic['grossprofit_margin_recent_deg2'] = np.where(2 <= roe_dt_year.shape[0], round(ABuRegUtil.calc_regress_deg(roe_dt_year.grossprofit_margin[0:2][::-1],show=False),4), np.nan)
            dic['grossprofit_margin_recent_deg3'] = np.where(3 <= roe_dt_year.shape[0], round(ABuRegUtil.calc_regress_deg(roe_dt_year.grossprofit_margin[0:3][::-1],show=False),4), np.nan)
            dic['debt_to_assets'] = df.iloc[0].debt_to_assets
            #dic['ts_code'] = df.iloc[0].ts_code
            return pd.Series(dic)
        return fin.groupby('ts_code').apply(_value_worth)