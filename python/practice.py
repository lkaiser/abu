#-*-coding:utf-8-*-
from abupy import AbuBenchmark, AbuCapital, ABuPickStockExecute, EMarketTargetType, AbuPickRegressAngMinMax, AbuPickStockShiftDistance, EMarketDataFetchMode
from abupy.CoreBu import ABuEnv
from abupy.PickStockBu import KPickStockValue, KPickStockStrongShake
from abupy.MarketBu.KSymbolFin import FinDataSource
import copy
import sys
from abupy.TradeBu.KFinManager import KFinManager


ABuEnv.g_market_target = EMarketTargetType.E_MARKET_TARGET_CN
#ABuEnv.enable_example_env_ipython()
def batchpick():


    #stock_pickers = [{'class': KPickStockValue,'first_choice':True,'start':'20180101','end':'20200526'},
    #                 {'class': KPickStockStrongShake, 'first_choice': True,'start':'20180101','end':'20200526', 'short_range': 30,'short_scope':1.15,'long_scope':1.6}]
    stock_pickers = [{'class': KPickStockValue,'first_choice':True,'start':'20180101','end':'20200526'}]
    #                  'threshold_ang_min': 0.0, 'reversed': False}]
    fin_manager = KFinManager()
    choice_symbols = fin_manager.get_stock_basic().ts_code.values()
    benchmark = AbuBenchmark()
    capital = AbuCapital(1000000, benchmark)

    print('ABuPickStockExecute.do_pick_stock_work:\n',
          ABuPickStockExecute.do_pick_stock_work(choice_symbols, benchmark, capital, stock_pickers))

#


if __name__ == '__main__':
    ABuEnv.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_NET
    batchpick()
    #ABuEnv.enable_example_env_ipython()
    #benchmark = AbuBenchmark()
    #print(benchmark.kl_pd)
