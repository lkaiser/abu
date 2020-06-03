#-*-coding:utf-8-*-
from abupy.UtilBu import ABuRegUtil
from .ABuPickStockBase import AbuPickStockBase
from ..SimilarBu.ABuCorrcoef import ECoreCorrType, corr_xy
import datetime
import pandas as pd

class KPickStockStrongShake(AbuPickStockBase):
    def _init_self(self, **kwargs):
        self.short_range = kwargs['short_range']
        self.short_scope = kwargs['short_scope']
        self.long_scope = kwargs['long_scope']
        self.start = kwargs['start']
        self.end = kwargs['end']

    def fit_pick(self, kl_pd, target_symbol):
        """精挑"""
        return True

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        """寻找趋势向上强于指数且振幅较大的"""
        # start = datetime.datetime.now().strftime("%Y%m%d")
        # end = (datetime.datetime.now() + datetime.timedelta(days=-365 * 2)).strftime("%Y%m%d")
        print(self.start)
        print(self.end)
        print(choice_symbols)
        daily = pick_worker.fin_manager.get_stock_daily(self.start[0:4]+self.start[4:6]+self.start[6:8],self.end[0:4]+self.end[4:6]+self.end[6:8],[symbol[0:6] for symbol in choice_symbols])
        daily.loc[:, 'date'] = daily.date.str.replace('-', '')  # tdx 与 tushare数据结构不一致，统一转化成yyyyMMdd格式
        adj = pick_worker.fin_manager.get_daily_adj(self.start,self.end,choice_symbols)
        adj.loc[:, 'code'] = adj.ts_code.str[0:6] # tdx 与 tushare数据结构不一致
        daily = daily.merge(adj, left_on=['date', 'code'],right_on=['trade_date', 'code'], how='left').sort_values(['ts_code', 'trade_date'], ascending=True)
        daily.loc[:, 'adj_close'] = daily.close * daily.adj_factor

        def _trend(df):
            dic = {}
            sdate = (datetime.datetime.strptime(self.end, "%Y%m%d")+ datetime.timedelta(days=-self.short_range)).strftime("%Y%m%d")
            ldate = (datetime.datetime.strptime(self.end, "%Y%m%d")+ datetime.timedelta(days=-400)).strftime("%Y%m%d")
            kl = df[df.trade_date > sdate].reset_index(drop=True)
            lkl = df[df.trade_date > ldate].reset_index(drop=True)
            if kl.shape[0] > 15:
                d_index = kl[['date', 'code']].merge(self.benchmark.kl_pd[['date', 'close', 'pre_close']], on=['date'],how='left')
                pre_close = kl.close.shift(1).values
                pre_close[0] = pre_close[1]
                kl.loc[:,'rise'] = ((kl.close/pre_close-1)*100).round(2)
                dic['short_range_deg'] = round(ABuRegUtil.calc_regress_deg(kl.adj_close,show=False),4)
                dic['short_range_shake'] = ((kl.high-kl.low)/kl.low).mean()
                benchmark_rise = d_index.close - d_index.pre_close
                dic['short_range_relation'] = round(corr_xy(kl.rise,benchmark_rise,ECoreCorrType.E_CORE_TYPE_PEARS),4)
                id = kl.adj_close.idxmax()
                dic['short_range_rise'] = (kl.iloc[id].adj_close-kl.iloc[0:id].adj_close.min())/kl.iloc[0:id].adj_close.min()
                lid = lkl.adj_close.idxmax()
                dic['long_range_rise'] = (lkl.iloc[id].adj_close - lkl.iloc[0:id].adj_close.min()) / lkl.iloc[0:lid].adj_close.min()
            return pd.Series(dic)
        print(daily.head())
        trend_status = daily.groupby('ts_code').apply(_trend)
        print(trend_status.head())
        trend_status = trend_status[~trend_status.short_range_shake.isnull()]
        benchmark_deg = round(ABuRegUtil.calc_regress_deg(self.benchmark.kl_pd.close,show=False),4)
        trend_status.loc['short_range_deg_diff'] = trend_status['short_range_deg']-benchmark_deg
        return trend_status[(trend_status.long_range_rise<1.6) & (trend_status.short_range_relation<-0.5) & (trend_status.short_range_shake>0.04) &(trend_status.short_range_deg_diff>0) & (trend_status.short_range_deg<0)].index.values.tolist()