#-*-coding:utf-8-*-
from abupy import abu
from abupy import AbuBenchmark, AbuCapital, ABuPickStockExecute, EMarketTargetType, AbuPickRegressAngMinMax, AbuPickStockShiftDistance, EMarketDataFetchMode
from abupy.CoreBu import ABuEnv
from abupy.PickStockBu import KPickStockValue, KPickStockStrongShake,KPickStockVolume
from abupy.MarketBu.KSymbolFin import FinDataSource
import copy
import sys
from abupy.TradeBu.KFinManager import KFinManager


ABuEnv.g_market_target = EMarketTargetType.E_MARKET_TARGET_CN
#ABuEnv.enable_example_env_ipython()
def batchpick():
    start = '20190101'
    end = '2020-11-06'
    # 策略 选取符合基本财务业绩指标，且短期与相关系数为负的，思路，庄股，跟大盘反着来的。这种策略适合在大盘下跌时买入
    stock_pickers = [{'class': KPickStockValue,'first_choice':True,'start':start,'end':end.replace('-',''),'roe_dt_2':13,'grossprofit_margin':20,'ocf_to_opincome':0.7},
                     {'class': KPickStockStrongShake, 'first_choice': True,'start':start,'end':end.replace('-',''),'short_relation':-0.25,'short_range': 30,'long_range': 300,'short_scope':1.15,'long_scope':1.7,'short_range_deg':5}]

    # 策略 选取符合基本财务业绩指标，最近1，2，3周成交量较大盘放大的，思路，选取资金涌入个股，改进（根据涌入个股分析所属板块，再延申选取相应板块优秀个股），自上而下的顺势根据当前资金涌入板块选择标的冲浪
    stock_pickers = [
        {'class': KPickStockValue, 'first_choice': True, 'start': start, 'end': end.replace('-', ''), 'roe_dt_2': 8,
         'grossprofit_margin': 18, 'ocf_to_opincome': 0.5},
        {'class': KPickStockVolume, 'first_choice': True, 'start': '20200801', 'end': end.replace('-', '')}]

    fin_manager = KFinManager()
    choice_symbols = fin_manager.get_stock_basic().ts_code
    #choice_symbols = ['688179.SH']
    benchmark = AbuBenchmark(start='2018-01-01',end=end)
    capital = AbuCapital(1000000, benchmark)

    print('ABuPickStockExecute.do_pick_stock_work:\n',
          ABuPickStockExecute.do_pick_stock_work(choice_symbols, benchmark, capital, stock_pickers))

#


if __name__ == '__main__':
    ABuEnv.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_NET
    batchpick()
    #run_kl_update这个方法必须先跑，加载kl_line 基础数据
    #abu.run_kl_update(start='2010-01-01', end='2020-12-26', market=EMarketTargetType.E_MARKET_TARGET_CN)
    #ABuEnv.enable_example_env_ipython()
    #benchmark = AbuBenchmark(start='2018-01-01',end='2020-05-18')
    #print(benchmark.kl_pd)
