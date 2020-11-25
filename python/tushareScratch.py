from abupy import FinDataSource

if __name__ == "__main__":
    ds = FinDataSource()
    #ds.save_stock_daily_basic()
    #ds.save_stock_daily()
    #ds.save_stock_adj_factor()
    ds.save_stock_report_income()
    ds.save_stock_report_assetliability()
    ds.save_stock_report_cashflow()
    ds.save_stock_report_forecast()
    ds.save_stock_report_express()
    ds.save_stock_report_dividend()