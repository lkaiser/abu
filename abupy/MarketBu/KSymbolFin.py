#-*-coding:utf-8-*-

from ..CoreBu import ABuEnv
import tushare as ts
import pandas as pd
import pymongo
import datetime
import time
import json


# import importlib,sys
# importlib.reload(sys)
# import sys
# reload(sys)
# sys.setdefaultencoding( "utf-8" )

class FinDataSource(object):
    def __init__(self):
        ts.set_token(ABuEnv.tushare_key)
        self.api = ts.pro_api()
        self.client = pymongo.MongoClient(host=ABuEnv.mongo_url,unicode_decode_error_handler='ignore').quantaxis
        self.INTERVAL = 0.2



    def save_stock_daily_basic(self,ind=0):
        '''
        获取每日指标，包含收盘价、换手率、量比、市盈率、市净率、股息率等信息
        '''
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
                print(e)
                time.sleep(30)
                daily = self.api.daily_basic(ts_code=df.iloc[i_].ts_code, start_date=start_date.replace("-", ""), end_date=today.replace("-", ""))
            print(" Get stock daily basic from tushare,days count is %d" % len(daily))
            if not daily.empty:
                # coll = client.stock_daily_basic_tushare
                # client.drop_collection(coll)
                # odo(daily, stock_daily)
                #json_data = QA_util_to_json_from_pandas(daily)
                json_data = json.loads(daily.to_json(orient='records'))
                stock_daily.insert_many(json_data)
            print(" Save data to stock_daily_basic_tushare collection， OK")

    def save_stock_daily(self,ind=0):
        '''
        每日行情
    输出参数

    名称	类型	描述
    ts_code	str	股票代码
    trade_date	str	交易日期
    open	float	开盘价
    high	float	最高价
    low	float	最低价
    close	float	收盘价
    pre_close	float	昨收价
    change	float	涨跌额
    pct_chg	float	涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
    vol	float	成交量 （手）
    amount	float	成交额 （千元）

                add by minijjlk

            在命令行工具 quantaxis 中输入 save stock_income 中的命令
            :param client:
            :return:
            '''
        pro = ts.pro_api()
        df = pro.stock_basic()
        if df.empty:
            print("there is no stock info,stock count is %d" % len(df))
            return
        report_income = self.client.stock_daily_tushare
        start_date = '20150101'
        today = datetime.datetime.now().strftime("%Y%m%d")
        print("##################get mainbz reports start####################")
        for i_ in range(ind,len(df.index)):
            print('The %s of Total %s' % (i_, len(df.index)))
            ref = report_income.find({'ts_code': df.iloc[i_].ts_code}).sort([('trade_date', -1)]).limit(1)
            if ref.count() > 0:
                start_date = pd.date_range((ref[0]['trade_date']), periods=2, freq='1d').strftime('%Y%m%d').values[-1]  # 取最新日期的下一天，所以，永远只有插入，没有更新
                print("start_date" + start_date.replace("-", "") + " today" + today.replace("-", ""))
                if start_date.replace("-", "") > today.replace("-", ""):
                    continue
            print('UPDATE stock daily basic Trying updating %s from %s to %s' % (df.iloc[i_].ts_code, start_date.replace("-", ""), today.replace("-", "")))
            time.sleep(self.INTERVAL)
            try:
                income = pro.daily(ts_code=df.iloc[i_].ts_code,start_date=start_date.replace("-", ""), end_date=today.replace("-", ""))
            except Exception as e:
                time.sleep(30)
                income = pro.daily(ts_code=df.iloc[i_].ts_code,start_date=start_date.replace("-", ""), end_date=today.replace("-", ""))
            finally:
                pass
            print(" Get stock daily from tushare,reports count is %d" % len(income))
            if not income.empty:
                # coll = client.stock_report_income_tushare
                # client.drop_collection(coll)
                json_data = json.loads(income.to_json(orient='records'))
                report_income.insert_many(json_data)
            print(" Save data to stock_daily_tushare collection， OK")

    def save_stock_adj_factor(self,start_day='20010101'):
        '''
        复权因子
    输出参数

    名称	类型	描述
    ts_code	str	股票代码
    trade_date	str	交易日期
    adj_factor	float	复权因子

                add by minijjlk

            在命令行工具 quantaxis 中输入 save stock_income 中的命令
            :param client:
            :return:
            '''
        pro = ts.pro_api()
        df = pro.stock_basic()
        if df.empty:
            print("there is no stock info,stock count is %d" % len(df))
            return
        report_income = self.client.stock_daily_adj_tushare
        start_date = '20150101'
        today = datetime.datetime.now().strftime("%Y%m%d")
        print("##################get mainbz reports start####################")
        for i_ in range(len(df.index)):
            print('The %s of Total %s' % (i_, len(df.index)))
            ref = report_income.find({'ts_code': df.iloc[i_].ts_code}).sort([('trade_date', -1)]).limit(1)
            if ref.count() > 0:
                start_date = pd.date_range((ref[0]['trade_date']), periods=2, freq='1d').strftime('%Y%m%d').values[ -1]  # 取最新日期的下一天，所以，永远只有插入，没有更新
                print("start_date" + start_date.replace("-", "") + " today" + today.replace("-", ""))
                if start_date.replace("-", "") > today.replace("-", ""):
                    continue
            print('UPDATE stock daily basic Trying updating %s from %s to %s' % (df.iloc[i_].ts_code, start_date.replace("-", ""), today.replace("-", "")))
            time.sleep(self.INTERVAL)
            try:
                income = pro.adj_factor(ts_code=df.iloc[i_].ts_code,start_date=start_date.replace("-", ""), end_date=today.replace("-", ""))
            except Exception as e:
                time.sleep(30)
                income = pro.adj_factor(ts_code=df.iloc[i_].ts_code,start_date=start_date.replace("-", ""), end_date=today.replace("-", ""))
            finally:
                pass
            print(" Get stock daily from tushare,reports count is %d" % len(income))
            if not income.empty:
                # coll = client.stock_report_income_tushare
                # client.drop_collection(coll)
                json_data = json.loads(income.to_json(orient='records'))
                report_income.insert_many(json_data)
            print(" Save data to stock_daily_adj_tushare collection， OK")

    def save_stock_report_income(self,start_day='20010101'):
        '''
        利润表数据
                输出参数

    名称	类型	描述
    ts_code	str	TS股票代码
    ann_date	str	公告日期
    f_ann_date	str	实际公告日期，即发生过数据变更的最终日期
    end_date	str	报告期
    report_type	str	报告类型： 参考下表说明
    comp_type	str	公司类型：1一般工商业 2银行 3保险 4证券
    basic_eps	float	基本每股收益
    diluted_eps	float	稀释每股收益
    total_revenue	float	营业总收入 (元，下同)
    revenue	float	营业收入
    int_income	float	利息收入
    prem_earned	float	已赚保费
    comm_income	float	手续费及佣金收入
    n_commis_income	float	手续费及佣金净收入
    n_oth_income	float	其他经营净收益
    n_oth_b_income	float	加:其他业务净收益
    prem_income	float	保险业务收入
    out_prem	float	减:分出保费
    une_prem_reser	float	提取未到期责任准备金
    reins_income	float	其中:分保费收入
    n_sec_tb_income	float	代理买卖证券业务净收入
    n_sec_uw_income	float	证券承销业务净收入
    n_asset_mg_income	float	受托客户资产管理业务净收入
    oth_b_income	float	其他业务收入
    fv_value_chg_gain	float	加:公允价值变动净收益
    invest_income	float	加:投资净收益
    ass_invest_income	float	其中:对联营企业和合营企业的投资收益
    forex_gain	float	加:汇兑净收益
    total_cogs	float	营业总成本
    oper_cost	float	减:营业成本
    int_exp	float	减:利息支出
    comm_exp	float	减:手续费及佣金支出
    biz_tax_surchg	float	减:营业税金及附加
    sell_exp	float	减:销售费用
    admin_exp	float	减:管理费用
    fin_exp	float	减:财务费用
    assets_impair_loss	float	减:资产减值损失
    prem_refund	float	退保金
    compens_payout	float	赔付总支出
    reser_insur_liab	float	提取保险责任准备金
    div_payt	float	保户红利支出
    reins_exp	float	分保费用
    oper_exp	float	营业支出
    compens_payout_refu	float	减:摊回赔付支出
    insur_reser_refu	float	减:摊回保险责任准备金
    reins_cost_refund	float	减:摊回分保费用
    other_bus_cost	float	其他业务成本
    operate_profit	float	营业利润
    non_oper_income	float	加:营业外收入
    non_oper_exp	float	减:营业外支出
    nca_disploss	float	其中:减:非流动资产处置净损失
    total_profit	float	利润总额
    income_tax	float	所得税费用
    n_income	float	净利润(含少数股东损益)
    n_income_attr_p	float	净利润(不含少数股东损益)
    minority_gain	float	少数股东损益
    oth_compr_income	float	其他综合收益
    t_compr_income	float	综合收益总额
    compr_inc_attr_p	float	归属于母公司(或股东)的综合收益总额
    compr_inc_attr_m_s	float	归属于少数股东的综合收益总额
    ebit	float	息税前利润
    ebitda	float	息税折旧摊销前利润
    insurance_exp	float	保险业务支出
    undist_profit	float	年初未分配利润
    distable_profit	float	可分配利润
    主要报表类型说明

    代码	类型	说明
    1	合并报表	上市公司最新报表（默认）
    2	单季合并	单一季度的合并报表
    3	调整单季合并表	调整后的单季合并报表（如果有）
    4	调整合并报表	本年度公布上年同期的财务报表数据，报告期为上年度
    5	调整前合并报表	数据发生变更，将原数据进行保留，即调整前的原数据
    6	母公司报表	该公司母公司的财务报表数据
    7	母公司单季表	母公司的单季度表
    8	母公司调整单季表	母公司调整后的单季表
    9	母公司调整表	该公司母公司的本年度公布上年同期的财务报表数据
    10	母公司调整前报表	母公司调整之前的原始财务报表数据
    11	调整前合并报表	调整之前合并报表原数据
    12	母公司调整前报表	母公司报表发生变更前保留的原数据

                add by minijjlk

            在命令行工具 quantaxis 中输入 save stock_income 中的命令
            :param client:
            :return:
            '''
        pro = ts.pro_api()
        df = pro.stock_basic()
        if df.empty:
            print("there is no stock info,stock count is %d" % len(df))
            return
        report_income = self.client.stock_report_income_tushare
        print("##################get income reports start####################")
        for i_ in range(len(df.index)):
            print('The %s of Total %s' % (i_, len(df.index)))
            ref = report_income.find({'ts_code': df.iloc[i_].ts_code})
            if ref.count() > 0:
                report_income.remove({'ts_code': df.iloc[i_].ts_code})
            print('UPDATE stock income Trying updating %s' % (df.iloc[i_].ts_code))
            time.sleep(1)
            try:
                income = pro.income(ts_code=df.iloc[i_].ts_code)
            except Exception as e:
                time.sleep(30)
                income = pro.income(ts_code=df.iloc[i_].ts_code)
            print(" Get stock income reports from tushare,reports count is %d" % len(income))
            if not income.empty:
                # coll = client.stock_report_income_tushare
                # client.drop_collection(coll)
                json_data = json.loads(income.to_json(orient='records'))
                report_income.insert_many(json_data)
            print(" Save data to stock_report_income_tushare collection， OK")

    def save_stock_report_assetliability(self,start_day='20010101'):
        '''
        资产负债表数据
    输出参数

    名称	类型	描述
    ts_code	str	TS股票代码
    ann_date	str	公告日期
    f_ann_date	str	实际公告日期
    end_date	str	报告期
    report_type	str	报表类型：见下方详细说明
    comp_type	str	公司类型：1一般工商业 2银行 3保险 4证券
    total_share	float	期末总股本
    cap_rese	float	资本公积金 (元，下同)
    undistr_porfit	float	未分配利润
    surplus_rese	float	盈余公积金
    special_rese	float	专项储备
    money_cap	float	货币资金
    trad_asset	float	交易性金融资产
    notes_receiv	float	应收票据
    accounts_receiv	float	应收账款
    oth_receiv	float	其他应收款
    prepayment	float	预付款项
    div_receiv	float	应收股利
    int_receiv	float	应收利息
    inventories	float	存货
    amor_exp	float	长期待摊费用
    nca_within_1y	float	一年内到期的非流动资产
    sett_rsrv	float	结算备付金
    loanto_oth_bank_fi	float	拆出资金
    premium_receiv	float	应收保费
    reinsur_receiv	float	应收分保账款
    reinsur_res_receiv	float	应收分保合同准备金
    pur_resale_fa	float	买入返售金融资产
    oth_cur_assets	float	其他流动资产
    total_cur_assets	float	流动资产合计
    fa_avail_for_sale	float	可供出售金融资产
    htm_invest	float	持有至到期投资
    lt_eqt_invest	float	长期股权投资
    invest_real_estate	float	投资性房地产
    time_deposits	float	定期存款
    oth_assets	float	其他资产
    lt_rec	float	长期应收款
    fix_assets	float	固定资产
    cip	float	在建工程
    const_materials	float	工程物资
    fixed_assets_disp	float	固定资产清理
    produc_bio_assets	float	生产性生物资产
    oil_and_gas_assets	float	油气资产
    intan_assets	float	无形资产
    r_and_d	float	研发支出
    goodwill	float	商誉
    lt_amor_exp	float	长期待摊费用
    defer_tax_assets	float	递延所得税资产
    decr_in_disbur	float	发放贷款及垫款
    oth_nca	float	其他非流动资产
    total_nca	float	非流动资产合计
    cash_reser_cb	float	现金及存放中央银行款项
    depos_in_oth_bfi	float	存放同业和其它金融机构款项
    prec_metals	float	贵金属
    deriv_assets	float	衍生金融资产
    rr_reins_une_prem	float	应收分保未到期责任准备金
    rr_reins_outstd_cla	float	应收分保未决赔款准备金
    rr_reins_lins_liab	float	应收分保寿险责任准备金
    rr_reins_lthins_liab	float	应收分保长期健康险责任准备金
    refund_depos	float	存出保证金
    ph_pledge_loans	float	保户质押贷款
    refund_cap_depos	float	存出资本保证金
    indep_acct_assets	float	独立账户资产
    client_depos	float	其中：客户资金存款
    client_prov	float	其中：客户备付金
    transac_seat_fee	float	其中:交易席位费
    invest_as_receiv	float	应收款项类投资
    total_assets	float	资产总计
    lt_borr	float	长期借款
    st_borr	float	短期借款
    cb_borr	float	向中央银行借款
    depos_ib_deposits	float	吸收存款及同业存放
    loan_oth_bank	float	拆入资金
    trading_fl	float	交易性金融负债
    notes_payable	float	应付票据
    acct_payable	float	应付账款
    adv_receipts	float	预收款项
    sold_for_repur_fa	float	卖出回购金融资产款
    comm_payable	float	应付手续费及佣金
    payroll_payable	float	应付职工薪酬
    taxes_payable	float	应交税费
    int_payable	float	应付利息
    div_payable	float	应付股利
    oth_payable	float	其他应付款
    acc_exp	float	预提费用
    deferred_inc	float	递延收益
    st_bonds_payable	float	应付短期债券
    payable_to_reinsurer	float	应付分保账款
    rsrv_insur_cont	float	保险合同准备金
    acting_trading_sec	float	代理买卖证券款
    acting_uw_sec	float	代理承销证券款
    non_cur_liab_due_1y	float	一年内到期的非流动负债
    oth_cur_liab	float	其他流动负债
    total_cur_liab	float	流动负债合计
    bond_payable	float	应付债券
    lt_payable	float	长期应付款
    specific_payables	float	专项应付款
    estimated_liab	float	预计负债
    defer_tax_liab	float	递延所得税负债
    defer_inc_non_cur_liab	float	递延收益-非流动负债
    oth_ncl	float	其他非流动负债
    total_ncl	float	非流动负债合计
    depos_oth_bfi	float	同业和其它金融机构存放款项
    deriv_liab	float	衍生金融负债
    depos	float	吸收存款
    agency_bus_liab	float	代理业务负债
    oth_liab	float	其他负债
    prem_receiv_adva	float	预收保费
    depos_received	float	存入保证金
    ph_invest	float	保户储金及投资款
    reser_une_prem	float	未到期责任准备金
    reser_outstd_claims	float	未决赔款准备金
    reser_lins_liab	float	寿险责任准备金
    reser_lthins_liab	float	长期健康险责任准备金
    indept_acc_liab	float	独立账户负债
    pledge_borr	float	其中:质押借款
    indem_payable	float	应付赔付款
    policy_div_payable	float	应付保单红利
    total_liab	float	负债合计
    treasury_share	float	减:库存股
    ordin_risk_reser	float	一般风险准备
    forex_differ	float	外币报表折算差额
    invest_loss_unconf	float	未确认的投资损失
    minority_int	float	少数股东权益
    total_hldr_eqy_exc_min_int	float	股东权益合计(不含少数股东权益)
    total_hldr_eqy_inc_min_int	float	股东权益合计(含少数股东权益)
    total_liab_hldr_eqy	float	负债及股东权益总计
    lt_payroll_payable	float	长期应付职工薪酬
    oth_comp_income	float	其他综合收益
    oth_eqt_tools	float	其他权益工具
    oth_eqt_tools_p_shr	float	其他权益工具(优先股)
    lending_funds	float	融出资金
    acc_receivable	float	应收款项
    st_fin_payable	float	应付短期融资款
    payables	float	应付款项
    hfs_assets	float	持有待售的资产
    hfs_sales	float	持有待售的负债
    主要报表类型说明

    代码	类型	说明
    1	合并报表	上市公司最新报表（默认）
    2	单季合并	单一季度的合并报表
    3	调整单季合并表	调整后的单季合并报表（如果有）
    4	调整合并报表	本年度公布上年同期的财务报表数据，报告期为上年度
    5	调整前合并报表	数据发生变更，将原数据进行保留，即调整前的原数据
    6	母公司报表	该公司母公司的财务报表数据
    7	母公司单季表	母公司的单季度表
    8	母公司调整单季表	母公司调整后的单季表
    9	母公司调整表	该公司母公司的本年度公布上年同期的财务报表数据
    10	母公司调整前报表	母公司调整之前的原始财务报表数据
    11	调整前合并报表	调整之前合并报表原数据
    12	母公司调整前报表	母公司报表发生变更前保留的原数据

                add by minijjlk

            在命令行工具 quantaxis 中输入 save stock_income 中的命令
            :param client:
            :return:
            '''
        pro = ts.pro_api()
        df = pro.stock_basic()
        if df.empty:
            print("there is no stock info,stock count is %d" % len(df))
            return
        report_income = self.client.stock_report_assetliability_tushare
        print("##################get asset liability reports start####################")
        for i_ in range(len(df.index)):
            print('The %s of Total %s' % (i_, len(df.index)))
            ref = report_income.find({'ts_code': df.iloc[i_].ts_code})
            if ref.count() > 0:
                report_income.remove({'ts_code': df.iloc[i_].ts_code})
            print('UPDATE stock asset liability Trying updating %s' % (df.iloc[i_].ts_code))
            time.sleep(1)
            try:
                income = pro.balancesheet(ts_code=df.iloc[i_].ts_code)
            except Exception as e:
                time.sleep(30)
                income = pro.balancesheet(ts_code=df.iloc[i_].ts_code)
            print(" Get stock asset liability reports from tushare,reports count is %d" % len(income))
            if not income.empty:
                # coll = client.stock_report_income_tushare
                # client.drop_collection(coll)
                json_data = json.loads(income.to_json(orient='records'))
                report_income.insert_many(json_data)
            print(" Save data to stock_report_assetliability_tushare collection， OK")

    def save_stock_report_cashflow(self,start_day='20010101'):
        '''
        现金流表数据
    输出参数

    名称	类型	描述
    ts_code	str	TS股票代码
    ann_date	str	公告日期
    f_ann_date	str	实际公告日期
    end_date	str	报告期
    comp_type	str	公司类型：1一般工商业 2银行 3保险 4证券
    report_type	str	报表类型：见下方详细说明
    net_profit	float	净利润 (元，下同)
    finan_exp	float	财务费用
    c_fr_sale_sg	float	销售商品、提供劳务收到的现金
    recp_tax_rends	float	收到的税费返还
    n_depos_incr_fi	float	客户存款和同业存放款项净增加额
    n_incr_loans_cb	float	向中央银行借款净增加额
    n_inc_borr_oth_fi	float	向其他金融机构拆入资金净增加额
    prem_fr_orig_contr	float	收到原保险合同保费取得的现金
    n_incr_insured_dep	float	保户储金净增加额
    n_reinsur_prem	float	收到再保业务现金净额
    n_incr_disp_tfa	float	处置交易性金融资产净增加额
    ifc_cash_incr	float	收取利息和手续费净增加额
    n_incr_disp_faas	float	处置可供出售金融资产净增加额
    n_incr_loans_oth_bank	float	拆入资金净增加额
    n_cap_incr_repur	float	回购业务资金净增加额
    c_fr_oth_operate_a	float	收到其他与经营活动有关的现金
    c_inf_fr_operate_a	float	经营活动现金流入小计
    c_paid_goods_s	float	购买商品、接受劳务支付的现金
    c_paid_to_for_empl	float	支付给职工以及为职工支付的现金
    c_paid_for_taxes	float	支付的各项税费
    n_incr_clt_loan_adv	float	客户贷款及垫款净增加额
    n_incr_dep_cbob	float	存放央行和同业款项净增加额
    c_pay_claims_orig_inco	float	支付原保险合同赔付款项的现金
    pay_handling_chrg	float	支付手续费的现金
    pay_comm_insur_plcy	float	支付保单红利的现金
    oth_cash_pay_oper_act	float	支付其他与经营活动有关的现金
    st_cash_out_act	float	经营活动现金流出小计
    n_cashflow_act	float	经营活动产生的现金流量净额
    oth_recp_ral_inv_act	float	收到其他与投资活动有关的现金
    c_disp_withdrwl_invest	float	收回投资收到的现金
    c_recp_return_invest	float	取得投资收益收到的现金
    n_recp_disp_fiolta	float	处置固定资产、无形资产和其他长期资产收回的现金净额
    n_recp_disp_sobu	float	处置子公司及其他营业单位收到的现金净额
    stot_inflows_inv_act	float	投资活动现金流入小计
    c_pay_acq_const_fiolta	float	购建固定资产、无形资产和其他长期资产支付的现金
    c_paid_invest	float	投资支付的现金
    n_disp_subs_oth_biz	float	取得子公司及其他营业单位支付的现金净额
    oth_pay_ral_inv_act	float	支付其他与投资活动有关的现金
    n_incr_pledge_loan	float	质押贷款净增加额
    stot_out_inv_act	float	投资活动现金流出小计
    n_cashflow_inv_act	float	投资活动产生的现金流量净额
    c_recp_borrow	float	取得借款收到的现金
    proc_issue_bonds	float	发行债券收到的现金
    oth_cash_recp_ral_fnc_act	float	收到其他与筹资活动有关的现金
    stot_cash_in_fnc_act	float	筹资活动现金流入小计
    free_cashflow	float	企业自由现金流量
    c_prepay_amt_borr	float	偿还债务支付的现金
    c_pay_dist_dpcp_int_exp	float	分配股利、利润或偿付利息支付的现金
    incl_dvd_profit_paid_sc_ms	float	其中:子公司支付给少数股东的股利、利润
    oth_cashpay_ral_fnc_act	float	支付其他与筹资活动有关的现金
    stot_cashout_fnc_act	float	筹资活动现金流出小计
    n_cash_flows_fnc_act	float	筹资活动产生的现金流量净额
    eff_fx_flu_cash	float	汇率变动对现金的影响
    n_incr_cash_cash_equ	float	现金及现金等价物净增加额
    c_cash_equ_beg_period	float	期初现金及现金等价物余额
    c_cash_equ_end_period	float	期末现金及现金等价物余额
    c_recp_cap_contrib	float	吸收投资收到的现金
    incl_cash_rec_saims	float	其中:子公司吸收少数股东投资收到的现金
    uncon_invest_loss	float	未确认投资损失
    prov_depr_assets	float	加:资产减值准备
    depr_fa_coga_dpba	float	固定资产折旧、油气资产折耗、生产性生物资产折旧
    amort_intang_assets	float	无形资产摊销
    lt_amort_deferred_exp	float	长期待摊费用摊销
    decr_deferred_exp	float	待摊费用减少
    incr_acc_exp	float	预提费用增加
    loss_disp_fiolta	float	处置固定、无形资产和其他长期资产的损失
    loss_scr_fa	float	固定资产报废损失
    loss_fv_chg	float	公允价值变动损失
    invest_loss	float	投资损失
    decr_def_inc_tax_assets	float	递延所得税资产减少
    incr_def_inc_tax_liab	float	递延所得税负债增加
    decr_inventories	float	存货的减少
    decr_oper_payable	float	经营性应收项目的减少
    incr_oper_payable	float	经营性应付项目的增加
    others	float	其他
    im_net_cashflow_oper_act	float	经营活动产生的现金流量净额(间接法)
    conv_debt_into_cap	float	债务转为资本
    conv_copbonds_due_within_1y	float	一年内到期的可转换公司债券
    fa_fnc_leases	float	融资租入固定资产
    end_bal_cash	float	现金的期末余额
    beg_bal_cash	float	减:现金的期初余额
    end_bal_cash_equ	float	加:现金等价物的期末余额
    beg_bal_cash_equ	float	减:现金等价物的期初余额
    im_n_incr_cash_equ	float	现金及现金等价物净增加额(间接法)
    主要报表类型说明

    代码	类型	说明
    1	合并报表	上市公司最新报表（默认）
    2	单季合并	单一季度的合并报表
    3	调整单季合并表	调整后的单季合并报表（如果有）
    4	调整合并报表	本年度公布上年同期的财务报表数据，报告期为上年度
    5	调整前合并报表	数据发生变更，将原数据进行保留，即调整前的原数据
    6	母公司报表	该公司母公司的财务报表数据
    7	母公司单季表	母公司的单季度表
    8	母公司调整单季表	母公司调整后的单季表
    9	母公司调整表	该公司母公司的本年度公布上年同期的财务报表数据
    10	母公司调整前报表	母公司调整之前的原始财务报表数据
    11	调整前合并报表	调整之前合并报表原数据
    12	母公司调整前报表	母公司报表发生变更前保留的原数据

                add by minijjlk

            在命令行工具 quantaxis 中输入 save stock_income 中的命令
            :param client:
            :return:
            '''
        pro = ts.pro_api()
        df = pro.stock_basic()
        if df.empty:
            print("there is no stock info,stock count is %d" % len(df))
            return
        report_income = self.client.stock_report_cashflow_tushare
        print("##################get asset cashflow reports start####################")
        for i_ in range(len(df.index)):
            print('The %s of Total %s' % (i_, len(df.index)))
            ref = report_income.find({'ts_code': df.iloc[i_].ts_code})
            if ref.count() > 0:
                report_income.remove({'ts_code': df.iloc[i_].ts_code})
            print('UPDATE stock cashflow Trying updating %s' % (df.iloc[i_].ts_code))
            time.sleep(1)
            try:
                income = pro.cashflow(ts_code=df.iloc[i_].ts_code)
            except Exception as e:
                time.sleep(30)
                income = pro.cashflow(ts_code=df.iloc[i_].ts_code)
            print(" Get stock cashflow reports from tushare,reports count is %d" % len(income))
            if not income.empty:
                # coll = client.stock_report_income_tushare
                # client.drop_collection(coll)
                json_data = json.loads(income.to_json(orient='records'))
                report_income.insert_many(json_data)
            print(" Save data to stock_report_cashflow_tushare collection， OK")

    def save_stock_report_forecast(self,start_year='2001'):
        '''
        业绩预告数据
    输出参数

    名称	类型	描述
    ts_code	str	TS股票代码
    ann_date	str	公告日期
    end_date	str	报告期
    type	str	业绩预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减)
    p_change_min	float	预告净利润变动幅度下限（%）
    p_change_max	float	预告净利润变动幅度上限（%）
    net_profit_min	float	预告净利润下限（万元）
    net_profit_max	float	预告净利润上限（万元）
    last_parent_net	float	上年同期归属母公司净利润
    first_ann_date	str	首次公告日
    summary	str	业绩预告摘要
    change_reason	str	业绩变动原因

                add by minijjlk

            在命令行工具 quantaxis 中输入 save stock_income 中的命令
            :param client:
            :return:
            '''
        pro = ts.pro_api()
        df = pro.stock_basic()
        if df.empty:
            print("there is no stock info,stock count is %d" % len(df))
            return
        report_forcast = self.client.stock_report_forcast_tushare
        print("##################get forcast reports start####################")
        today = datetime.datetime.now().strftime("%Y%m%d")
        season = ['0331', '0630', '0930', '1231']
        years = range(int(start_year[0, 4]), int(today[0:4]))
        for i_ in range(len(df.index)):
            print('The %s of Total %s' % (i_, len(df.index)))
            start_date = start_year
            time.sleep(1)
            ref = report_forcast.find({'ts_code': df.iloc[i_].ts_code, 'trade_date': {'$regex': '^2019'}})
            if ref.count() > 0:
                report_forcast.remove({'ts_code': df.iloc[i_].ts_code, 'trade_date': {'$regex': '^2019'}})
            print('UPDATE stock forcast report Trying updating %s from %s' % (
            df.iloc[i_].ts_code, start_date.replace("-", "")))
            forcasts = []
            try:
                for y in years:
                    for s in season:
                        time.sleep(1)
                        f = pro.forcast(ts_code=df.iloc[i_].ts_code, period=str(y) + s)
                        if not f.empty:
                            forcasts.append(f)
            except Exception as e:
                print(e)
                time.sleep(30)
                continue
            print(" Get stock forcast reports from tushare,reports count is %d" % len(forcasts))
            if not forcasts:
                json_data = json.loads(forcasts.to_json(orient='records'))
                forcasts.insert_many(json_data)
            print(" Save data to stock_report_forcast_tushare collection， OK")

    def save_stock_report_express(self,start_day='20010101'):
        '''
        业绩快报数据
    输出参数

    名称	类型	描述
    ts_code	str	TS股票代码
    ann_date	str	公告日期
    end_date	str	报告期
    revenue	float	营业收入(元)
    operate_profit	float	营业利润(元)
    total_profit	float	利润总额(元)
    n_income	float	净利润(元)
    total_assets	float	总资产(元)
    total_hldr_eqy_exc_min_int	float	股东权益合计(不含少数股东权益)(元)
    diluted_eps	float	每股收益(摊薄)(元)
    diluted_roe	float	净资产收益率(摊薄)(%)
    yoy_net_profit	float	去年同期修正后净利润
    bps	float	每股净资产
    yoy_sales	float	同比增长率:营业收入
    yoy_op	float	同比增长率:营业利润
    yoy_tp	float	同比增长率:利润总额
    yoy_dedu_np	float	同比增长率:归属母公司股东的净利润
    yoy_eps	float	同比增长率:基本每股收益
    yoy_roe	float	同比增减:加权平均净资产收益率
    growth_assets	float	比年初增长率:总资产
    yoy_equity	float	比年初增长率:归属母公司的股东权益
    growth_bps	float	比年初增长率:归属于母公司股东的每股净资产
    or_last_year	float	去年同期营业收入
    op_last_year	float	去年同期营业利润
    tp_last_year	float	去年同期利润总额
    np_last_year	float	去年同期净利润
    eps_last_year	float	去年同期每股收益
    open_net_assets	float	期初净资产
    open_bps	float	期初每股净资产
    perf_summary	str	业绩简要说明
    is_audit	int	是否审计： 1是 0否
    remark	str	备注

                add by minijjlk

            在命令行工具 quantaxis 中输入 save stock_income 中的命令
            :param client:
            :return:
            '''
        pro = ts.pro_api()
        df = pro.stock_basic()
        if df.empty:
            print("there is no stock info,stock count is %d" % len(df))
            return
        report_income = self.client.stock_report_express_tushare
        print("##################get express reports start####################")
        for i_ in range(len(df.index)):
            print('The %s of Total %s' % (i_, len(df.index)))
            ref = report_income.find({'ts_code': df.iloc[i_].ts_code})
            if ref.count() > 0:
                report_income.remove({'ts_code': df.iloc[i_].ts_code})
            print('UPDATE stock express Trying updating %s' % (df.iloc[i_].ts_code))
            time.sleep(1)
            try:
                income = pro.express(ts_code=df.iloc[i_].ts_code)
            except Exception as e:
                time.sleep(30)
                income = pro.express(ts_code=df.iloc[i_].ts_code)
            print(" Get stock express reports from tushare,reports count is %d" % len(income))
            if not income.empty:
                # coll = client.stock_report_income_tushare
                # client.drop_collection(coll)
                json_data = json.loads(income.to_json(orient='records'))
                # json_data = json.loads(df.reset_index().to_json(orient='records'))
                report_income.insert_many(json_data)
            print(" Save data to stock_report_express_tushare collection， OK")

    def QA_SU_save_stock_report_dividend(self,start_day='20010101'):
        '''
        分红送股数据
    输出参数

    名称	类型	默认显示	描述
    ts_code	str	Y	TS代码
    end_date	str	Y	分红年度
    ann_date	str	Y	预案公告日
    div_proc	str	Y	实施进度
    stk_div	float	Y	每股送转
    stk_bo_rate	float	Y	每股送股比例
    stk_co_rate	float	Y	每股转增比例
    cash_div	float	Y	每股分红（税后）
    cash_div_tax	float	Y	每股分红（税前）
    record_date	str	Y	股权登记日
    ex_date	str	Y	除权除息日
    pay_date	str	Y	派息日
    div_listdate	str	Y	红股上市日
    imp_ann_date	str	Y	实施公告日
    base_date	str	N	基准日
    base_share	float	N	基准股本（万）

                add by minijjlk

            在命令行工具 quantaxis 中输入 save stock_income 中的命令
            :param client:
            :return:
            '''
        pro = ts.pro_api()
        df = pro.stock_basic()
        if df.empty:
            print("there is no stock info,stock count is %d" % len(df))
            return
        report_income = self.client.stock_report_dividend_tushare
        print("##################get dividend reports start####################")
        for i_ in range(len(df.index)):
            print('The %s of Total %s' % (i_, len(df.index)))
            ref = report_income.find({'ts_code': df.iloc[i_].ts_code})
            if ref.count() > 0:
                report_income.remove({'ts_code': df.iloc[i_].ts_code})
            print('UPDATE stock dividend Trying updating %s' % (df.iloc[i_].ts_code))
            time.sleep(1)
            try:
                income = pro.dividend(ts_code=df.iloc[i_].ts_code)
            except Exception as e:
                time.sleep(30)
                income = pro.dividend(ts_code=df.iloc[i_].ts_code)
            print(" Get stock dividend reports from tushare,reports count is %d" % len(income))
            if not income.empty:
                # coll = client.stock_report_income_tushare
                # client.drop_collection(coll)
                json_data = json.loads(income.to_json(orient='records'))
                # json_data = json.loads(df.reset_index().to_json(orient='records'))
                report_income.insert_many(json_data)
            print(" Save data to stock_report_express_tushare collection， OK")

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
        cursor = self.client.stock_day.find(query, {"_id": 0}, batch_size=10000)
        return pd.DataFrame([item for item in cursor]).sort_values(['code', 'date'], ascending=True)

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



