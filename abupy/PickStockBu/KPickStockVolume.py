#-*-coding:utf-8-*-
from .ABuPickStockBase import AbuPickStockBase, reversed_result

__author__ = 'K'

from ..UtilBu import ABuRegUtil
import pandas as pd


class KPickStockVolume(AbuPickStockBase):
    """ 量价指标，寻找成交量逐步放大，相对大盘成交量放大，以最近1、2、3、4、5周来看，"""
    def _init_self(self, **kwargs):
        """通过kwargs设置位条件，配置因子参数"""
        self.start = kwargs['start']
        self.end = kwargs['end']

    def fit_pick(self, kl_pd, target_symbol):
        """精挑"""
        return True

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        daily = pick_worker.fin_manager.get_stock_daily(self.start,self.end,[symbol for symbol in choice_symbols])
        adj = pick_worker.fin_manager.get_daily_adj(self.start, self.end, choice_symbols)
        daily = daily.merge(adj, left_on=['trade_date', 'ts_code'], right_on=['trade_date', 'ts_code'],
                            how='left').sort_values(['ts_code', 'trade_date'], ascending=True)
        daily.loc[:, 'adj_close'] = daily.close * daily.adj_factor
        #print(daily.head())

        def _trend(df):
            dic = {}
            # 3周以上数据改为用周线
            if df.shape[0]>30: #30条数据都没有，就不要玩了
                df = df.set_index(pd.DatetimeIndex(pd.to_datetime(df.trade_date)))
                if 'adj_close' not in df.columns.values:
                    df.loc[:, 'adj_close'] = df.close
                week_data = df.resample('W').last()
                week_data['open'] = df['open'].resample('W').first()
                week_data['high'] = df['high'].resample('W').max()
                week_data['low'] = df['low'].resample('W').min()
                week_data['vol'] = df['vol'].resample('W').sum()


                dic['week_1_deg'] = ABuRegUtil.calc_regress_deg(df.vol.iloc[-5:], show=False)
                dic['week_2_deg'] = ABuRegUtil.calc_regress_deg(df.vol.iloc[-10:], show=False)
                dic['week_3_deg'] = ABuRegUtil.calc_regress_deg(week_data.vol.iloc[-3:], show=False)
                dic['week_4_deg'] = ABuRegUtil.calc_regress_deg(week_data.vol.iloc[-4:], show=False)
                dic['week_5_deg'] = ABuRegUtil.calc_regress_deg(week_data.vol.iloc[-5:], show=False)

                dic['week_1_rise'] = df.adj_close[-1]/df.adj_close[-5]
                dic['week_2_rise'] = df.adj_close[-1] / df.adj_close[-10]
                dic['week_3_rise'] = week_data.adj_close[-1] / week_data.adj_close[-3]
                dic['week_4_rise'] = week_data.adj_close[-1] / week_data.adj_close[-4]
                dic['week_5_rise'] = week_data.adj_close[-1] / week_data.adj_close[-5]
                return pd.Series(dic)

        benchmark = self.benchmark.kl_pd[self.benchmark.kl_pd.trade_date>=self.start]
        index_trend_status = benchmark.groupby('ts_code').apply(_trend)
        rs = daily.groupby('ts_code').apply(_trend)
        rs2 = rs.reset_index()
        print(index_trend_status.describe())
        print(rs2[rs2.ts_code=='603197.SH'])
        rs = rs[((rs.week_1_deg>index_trend_status.iloc[0].week_1_deg) & (rs.week_1_deg>10)) | ((rs.week_3_deg>index_trend_status.iloc[0].week_3_deg) & (rs.week_3_deg>10))] #大于指数且大于0才有意义

        #rs = rs[(rs.week_2_deg>5)]
        rs = rs[(rs.week_1_rise<index_trend_status.iloc[0].week_1_rise)] #涨幅也要低于大盘
        return rs.index.values.tolist()
        #return list(set(fin.index.values).intersection(set(choice_symbols))) if (choice_symbols is not None and len(choice_symbols) > 0) else fin.index.values.list()

