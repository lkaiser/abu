#-*-coding:utf-8-*-
from abupy.UtilBu import ABuRegUtil
from .ABuPickStockBase import AbuPickStockBase
from ..SimilarBu.ABuCorrcoef import ECoreCorrType, corr_xy
import datetime
import pandas as pd
import numpy as np
import logging

from ..TLineBu.ABuTLine import AbuTLine


class KPickStockStrongShake(AbuPickStockBase):
    """形态选股，选取符合趋势线角度，长短期涨跌幅在一定阈值范围内的股票，根据振幅，相关性，通道位置百分比等指标过滤
        short_scope 短期涨幅，例 1.1，1.2
        short_range 短期时间区间 days 30,60
        short_relation 短期相关系数  -1 - 1
        short_shake 短期日内震幅，用（当日最高-当日最低）/当日最低再取区间均值，在短期涨幅限定的情况下，shake越大，说明日内振幅越大
        shift_distance 短期位移路程比，short_shake 是计算日内振幅均值，shift_distance是计算区间振幅均值
        short_range_deg 短期趋势角度（无需和大盘比较，好的个股，大盘向下时，他能平着走，大盘上涨时，蓄势待发的，所以，趋势角度取绝对，不能相对大盘）
        long_scope 长期涨幅 例 1.5  2
        long_range 长期区间 days 200,300
    """
    def __str__(self):
        return "KPickStockStrongShake a"
    def _init_self(self, **kwargs):
        self.short_range = kwargs['short_range']
        self.short_scope = kwargs['short_scope']
        self.long_range = kwargs['long_range']
        self.long_scope = kwargs['long_scope']
        self.short_relation = kwargs['short_relation'] if 'short_relation' in kwargs else None
        self.short_shake = kwargs['short_shake'] if 'short_shake' in kwargs else None
        self.shift_distance = kwargs['shift_distance'] if 'shift_distance' in kwargs else None
        self.short_range_deg = kwargs['short_range_deg'] if 'short_range_deg' in kwargs else None
        self.start = kwargs['start']
        self.end = kwargs['end']

    def fit_pick(self, kl_pd, target_symbol):
        """精挑，"""

        return True

    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        """寻找趋势向上强于指数且振幅较大的,振幅既可指日内振幅，也可指区间振幅"""
        # start = datetime.datetime.now().strftime("%Y%m%d")
        # end = (datetime.datetime.now() + datetime.timedelta(days=-365 * 2)).strftime("%Y%m%d")
        daily = pick_worker.fin_manager.get_stock_daily(self.start,self.end,[symbol for symbol in choice_symbols])
        #daily.loc[:, 'date'] = daily.trade_date.str.replace('-', '')  # tdx 与 tushare数据结构不一致，统一转化成yyyyMMdd格式
        adj = pick_worker.fin_manager.get_daily_adj(self.start,self.end,choice_symbols)
        logging.info('############ the choince symbos is :{}'.format(choice_symbols))
        #adj.loc[:, 'code'] = adj.ts_code.str[0:6] # tdx 与 tushare数据结构不一致
        daily = daily.merge(adj, left_on=['trade_date', 'ts_code'],right_on=['trade_date', 'ts_code'], how='left').sort_values(['ts_code', 'trade_date'], ascending=True)
        daily.loc[:, 'adj_close'] = daily.close * daily.adj_factor
        sdate = (datetime.datetime.strptime(self.end, "%Y%m%d") + datetime.timedelta(days=-self.short_range)).strftime("%Y%m%d")
        ldate = (datetime.datetime.strptime(self.end, "%Y%m%d") + datetime.timedelta(days=-self.long_range)).strftime("%Y%m%d")

        daily2 = daily[['trade_date', 'ts_code']].merge(self.benchmark.kl_pd[['trade_date', 'close', 'pre_close']], on=['trade_date'], how='left')
        daily.loc[:,'benchmark_rise'] = ((daily2.close / daily2.pre_close - 1) * 100).round(2) #有点错误，不要紧，每只code第一天的rise肯定是错的，因为没分组算

        pre_close = daily.close.shift(1).values
        pre_close[0] = pre_close[1]
        daily.loc[:, 'rise'] = ((daily.close / pre_close - 1) * 100).round(2)  #有点错误，不要紧，每只code第一天的rise肯定是错的，因为没分组算

        #dic['short_range_relation'] = round(corr_xy(daily.rise, daily.benchmark_rise, ECoreCorrType.E_CORE_TYPE_PEARS), 4)

        def _trend(df):
            dic = {}
            kl = df[df.trade_date > sdate].reset_index(drop=True)
            lkl = df[df.trade_date > ldate].reset_index(drop=True)
            #print('##########df max trade_date {} , sdate {}, ldate {}'.format(df.trade_date.max(),sdate,ldate))
            if kl.shape[0] > 15: #数据量不大于15天没有什么参考意义，其实大于20天也就是4周以上才有比较意义
                #d_index = kl[['date', 'code']].merge(self.benchmark.kl_pd[['date', 'close', 'pre_close']], on=['date'],how='left')
                #pre_close = kl.close.shift(1).values
                #pre_close[0] = pre_close[1]
                #kl.loc[:,'rise'] = ((kl.close/pre_close-1)*100).round(2)
                model, _ = ABuRegUtil.regress_y(kl.adj_close, mode=True, zoom=True, show=False)
                rad = model.params[1]
                dic['short_range_deg'] = round(np.rad2deg(rad),4) #两种思路， 1 要求至少最近20天符合某种趋势，则称为短期角度 2 拟合曲线，找到最近拐点，距今超过20天也可以
                dic['short_range_rsquare'] = model.rsquared
                dic['short_range_shake'] = ((kl.high-kl.low)/kl.low).mean()
                #benchmark_rise = ((d_index.close/d_index.pre_close-1)*100).round(2)
                cor_count = 10 if 10<=(df.shape[0]-kl.shape[0]) else (df.shape[0]-kl.shape[0])
                print('########## cor_count = {}'.format(cor_count))
                relation_arr = [round(corr_xy(df.iloc[-(kl.shape[0]+i):-i].rise.values, df.iloc[-(kl.shape[0]+i):-i].benchmark_rise.values, ECoreCorrType.E_CORE_TYPE_PEARS), 4) for i in range(1,cor_count)]
                dic['short_range_relation'] = min(relation_arr) if relation_arr else None #前20天的relaition 取最小值，因为 relation主要是取30天的，已经做了平滑处理，再取前20天是因为信号不是一出来就有机会，后续需要根据位置判断
                #dic['short_range_relation'] = round(corr_xy(kl.rise,benchmark_rise,ECoreCorrType.E_CORE_TYPE_PEARS),4)
                pick_line = AbuTLine(kl.close, 'shift distance')
                dic['shift_distance'] = pick_line.show_shift_distance(step_x=1.0, show_log=False, show=False)[4]
                id = kl.adj_close.idxmax()
                dic['short_range_rise'] = (kl.iloc[id].adj_close-kl.iloc[0:id].adj_close.min())/kl.iloc[0:id].adj_close.min()
                lid = lkl.adj_close.idxmax()
                dic['long_range_rise'] = (lkl.iloc[lid].adj_close - lkl.iloc[0:lid].adj_close.min()) / lkl.iloc[0:lid].adj_close.min()
                return pd.Series(dic)
        trend_status = daily.groupby('ts_code').apply(_trend)
        if trend_status.shape[0] >0:
            print(trend_status.describe())
            trend_status = trend_status[~trend_status.short_range_shake.isnull()]
            trend_status = trend_status[(trend_status.long_range_rise<self.long_scope) & (trend_status.short_range_rise<self.short_scope)]
            if self.short_relation is not None:
                trend_status = trend_status[trend_status.short_range_relation < self.short_relation]
            if self.short_shake is not None:
                trend_status = trend_status[trend_status.short_range_shake > self.short_shake]
            if self.short_range_deg is not None:
                trend_status = trend_status[(trend_status.short_range_deg < (self.short_range_deg+2)) & (trend_status.short_range_rise > (self.short_scope-2))] #选取符合短期趋势+-2°范围的,且判定系数大于0.7 这样至少大致能拟合出条直线的那种图形
        return trend_status.index.values.tolist()