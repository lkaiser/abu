from abupy import FinDataSource

if __name__ == "__main__":
    ds = FinDataSource()
    #ds.save_index()
    #ds.save_index_daily(ind=350)
    #ds.save_stock_daily_basic()
    #ds.save_stock_daily(ind=2128)
    ds.save_stock_report_indicator()
    # ds.save_stock_adj_factor()
    # ds.save_stock_report_income()
    #ds.save_stock_report_assetliability(ind=281)
    #ds.save_stock_report_cashflow()
    # ds.save_stock_report_forecast()
    # ds.save_stock_report_express()
    # ds.save_stock_report_dividend()