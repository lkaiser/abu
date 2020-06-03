#-*-coding:utf-8-*-

from ..CoreBu import ABuEnv
import tushare as ts
import pandas as pd
import pymongo
import datetime
import time
import json
from odo import odo

import importlib,sys
importlib.reload(sys)

class FinDataSource(object):
    def __init__(self):
        ts.set_token(ABuEnv.tushare_key)
        self.api = ts.pro_api()
        self.client = pymongo.MongoClient(host=ABuEnv.mongo_url,unicode_decode_error_handler='ignore').quantaxis
        self.INTERVAL = 0.2


    def save_stock_daily_basic(self,ind,start, end):
        df = self.api.stock_basic()
        if df.empty:
            print("there is no stock info,stock count is %d" % len(df))
            return
        stock_daily = self.client.stock_daily_basic_tushare
        today = datetime.datetime.now().strftime("%Y%m%d")
        for i_ in range(ind, len(df.index)):
            ref = stock_daily.find({'ts_code': df.iloc[i_].ts_code}).sort([('trade_date', -1)]).limit(1)
            if ref.count() > 0:
                start_date = pd.date_range((ref[0]['trade_date']), periods=2, freq='1d').strftime('%Y%m%d').values[-1]  # 取最新日期的下一天，所以，永远只有插入，没有更新
                print("start_date" + start_date.replace("-", "") + " today" + today.replace("-", ""))
                if start_date.replace("-", "") > today.replace("-", ""):
                    continue
            print('UPDATE stock daily basic Trying updating %s from %s to %s' % (df.iloc[i_].ts_code, start_date.replace("-", ""), today.replace("-", "")))
            time.sleep(self.INTERVAL)
            try:
                daily = self.api.daily_basic(ts_code=df.iloc[i_].ts_code, start_date=start_date.replace("-", ""), end_date=today.replace("-", ""))
            except Exception as e:
                time.sleep(30)
                daily = self.api.daily_basic(ts_code=df.iloc[i_].ts_code, start_date=start_date.replace("-", ""), end_date=today.replace("-", ""))
            print(" Get stock daily basic from tushare,days count is %d" % len(daily))
            if not daily.empty:
                # coll = client.stock_daily_basic_tushare
                # client.drop_collection(coll)
                odo(daily, stock_daily)
                # json_data = json.loads(df.reset_index().to_json(orient='records'))
            print(" Save data to stock_daily_basic_tushare collection， OK")

    def get_stock_basic(self):
        return self.api.stock_basic()

    def get_index_daily(self,start, end, code=None):
        query = {"date": {
            "$lte": end,
            "$gte": start}}
        if code:
            query['code'] = {'$in': code}
        cursor = self.client.index_day.find(query, {"_id": 0}, batch_size=10000).sort([("code",1),("date",1)])
        return pd.DataFrame([item for item in cursor])

    def get_stock_daily(self,start, end, code=None):
        query = {"date": {
            "$lte": end,
            "$gte": start}}
        if code:
            query['code'] = {'$in': code}
        cursor = self.client.stock_day.find(query, {"_id": 0}, batch_size=10000).sort([("code",1),("date",1)])
        return pd.DataFrame([item for item in cursor])

    def get_stock_daily_basic(self,start, end, code=None):
        query = {"trade_date": {
            "$lte": end,
            "$gte": start}}
        if code:
            query['ts_code'] = {'$in': code}
        cursor = self.client.stock_daily_basic_tushare.find(query, {"_id": 0}, batch_size=10000)  # .sort([("ts_code",1),("trade_date",1)])
        return pd.DataFrame([item for item in cursor]).sort_values(['ts_code', 'trade_date'], ascending=True)

    def get_assetAliability(self,start, end, code=None):
        query = {"end_date": {
            "$lte": end,
            "$gte": start}}
        if code:
            query['ts_code'] = {'$in': code}
        cursor = self.client.sstock_report_assetliability_tushare.find(query, {"_id": 0}, batch_size=10000)  # .sort([("ts_code",1),("end_date",1)])

        return pd.DataFrame([item for item in cursor]).sort_values(['ts_code', 'end_date'], ascending=True)

    def get_cashflow(self,start, end, code=None):
        query = {"end_date": {
            "$lte": end,
            "$gte": start}}
        if code:
            query['ts_code'] = {'$in': code}
        cursor = self.client.stock_report_cashflow_tushare.find(query, {"_id": 0}, batch_size=10000)  # .sort([("ts_code",1),("end_date",1)])
        # df = pd.DataFrame([item for item in cursor])
        # print(df.head())
        return pd.DataFrame([item for item in cursor]).sort_values(['ts_code', 'end_date'], ascending=True)

    def get_income(self,start, end, code=None):
        query = {"end_date": {
            "$lte": end,
            "$gte": start}}
        if code:
            query['ts_code'] = {'$in': code}
        cursor = self.client.stock_report_income_tushare.find(query, {"_id": 0}, batch_size=10000)  # .sort([("ts_code",1),("end_date",1)])

        return pd.DataFrame([item for item in cursor]).sort_values(['ts_code', 'end_date'], ascending=True)


    def get_daily_adj(self,start, end, code=None):
        query = {"trade_date": {
            "$lte": end,
            "$gte": start}}
        if code:
            query['ts_code'] = {'$in': code}
        cursor = self.client.stock_daily_adj_tushare.find(query, {"_id": 0}, batch_size=10000)  # .sort([("ts_code",1),("trade_date",1)])

        return pd.DataFrame([item for item in cursor]).sort_values(['ts_code', 'trade_date'], ascending=True)

    def get_money_flow(self,start, end, code=None):
        query = {"trade_date": {
            "$lte": end,
            "$gte": start}}
        if code:
            query['ts_code'] = {'$in': code}
        cursor = self.client.stock_daily_moneyflow_tushare.find(query, {"_id": 0}, batch_size=10000)  # .sort([("ts_code",1),("trade_date",1)])

        return pd.DataFrame([item for item in cursor]).sort_values(['ts_code', 'trade_date'], ascending=True)

    def get_finindicator(self,start, end, code=None):
        query = {"end_date": {
            "$lte": end,
            "$gte": start}}
        if code:
            query['ts_code'] = {'$in': code}
        cursor = self.client.stock_report_finindicator_tushare.find(query, {"_id": 0}, batch_size=10000)  # .sort([("ts_code",1),("end_date",1)])
        data = []
        i = 0
        for post in cursor:
            i = i + 1
            data.append(post)
        return pd.DataFrame(data).sort_values(['ts_code', 'end_date'], ascending=True)




