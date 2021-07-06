import yahoo_fin.stock_info as yf
import os
import numpy as np
import pandas as pd
import requests
import FundamentalAnalysis as fa
from .DB import database as db
from sqlite3 import Error


class stock_data():
    def __init__(self,ticker=None,api_key=None,period=None,interval=None,begin_date=None,end_date=None,bool_choice=False):
        self.ticker,self.period,self.interval,self.begin_date,self.end_date=ticker,period,interval,begin_date,end_date
        self.api_key=api_key
        self.bool_choice=bool_choice
        self.function_mapper={"dividend":self.get_dividend, "profile":self.get_profile, "quote":self.get_quote,
                                "rating":self.get_rating,"dcf":self.get_dcf,"metric":self.get_metrics,"ratio":self.get_ratios,
                                "data":self.get_data,"detailed_data":self.get_detail_data,"list":self.show_all_comp}

    def get_dividend(self):
        func_name="dividends"
        dividends=pd.DataFrame(fa.stock_dividend(self.ticker, self.api_key, begin=self.begin_date, end=self.end_date))
        div_to_sql=dividends.to_sql(f"{self.ticker}_{func_name}",db().conn,index=False,if_exists="replace")
        return {"functionName":"dividend","result":dividends,"msg_log":f"Added {func_name} to database for {self.ticker}"}

    def show_all_comp(self):
        # Show the available companies
        companies=pd.DataFrame(fa.available_companies(self.api_key))
        cie_to_Sql=companies.to_sql("listed_companies", db().conn, if_exists="replace", index=True, index_label="symbol")
        return {"functionName":"list","result":companies,"msg_log":"Added all listed companies to database"}

    def get_profile(self):
        func_name="profile"
        # Collect general company information
        profile=pd.DataFrame(fa.profile(self.ticker, self.api_key))
        profile=profile.set_index("symbol")
        msg_log=f"Added {func_name} to database for {self.ticker}"
        try:
            profile_to_sql=profile.to_sql(func_name, db().conn, if_exists="append", index=True,index_label="symbol")
        except Error as e:
            db().query_executor()
            msg_log=f"{e}"
        return {"functionName":func_name,"result":profile,"msg_log":msg_log}

    def get_quote(self):
        func_name="quote"
        # Collect recent company quotes
        quote=pd.DataFrame(fa.quote(self.ticker, self.api_key))
        #quote_to_sql=quote.to_sql("quote", db().conn, if_exists="replace", index=False)
        r=quote.to_records()
        r=list(r[0])
        print(str(r).strip("[").strip("]"))
        return {"functionName":func_name,"result":quote,"Msg_log":f"Added {func_name} to database for {self.ticker}"}

    def get_mkt_cap(self):
        # Collect market cap and enterprise value
        return fa.enterprise(self.ticker, self.api_key)

    def get_rating(self):
        func_name="rating"
        # Show recommendations of Analysts
        rating=fa.rating(self.ticker, self.api_key)
        rating_to_sql=rating.to_sql(f"{self.ticker}_{func_name}", db().conn, if_exists="replace", index=False)
        return {"functionName":func_name,"result":rating,"msg_log":f"Added {func_name} to database for {self.ticker}"}

    def get_dcf(self,period):
        # Obtain DCFs over time
        return fa.discounted_cash_flow(self.ticker, self.api_key, period=period)
        
    def get_balance(self,period):
        # Collect the Balance Sheet statements
        return fa.balance_sheet_statement(self.ticker, self.api_key, period=period)
    
    def get_income(self,period):
        # Collect the Income Statements
        return fa.income_statement(self.ticker, self.api_key, period=period)
        
    def get_cash_flow(self,period):
        # Collect the Cash Flow Statements
        return fa.cash_flow_statement(self.ticker, self.api_key, period=period)
      
    def get_metrics(self,period):
        # Show Key Metrics
        return fa.key_metrics(self.ticker, self.api_key, period=period)
       
    def get_ratios(self,period):
        # Show a large set of in-depth ratios
        return fa.financial_ratios(self.ticker, self.api_key, period=period)
        
    def get_growth(self,period):
        # Show the growth of the company
        return fa.financial_statement_growth(self.ticker, self.api_key, period=period)
      
    def get_data(self,period,interval):
        # Download general stock data
        return fa.stock_data(self.ticker, period=period, interval=interval)
    def get_detail_data(self,begin_date,end_date):
        # Download detailed stock data
        return fa.stock_data_detailed(self.ticker, self.api_key, begin=begin_date, end=end_date)

class ticker_list_parser():
    def __init__(self,list):
        self.ticker_list=[]
        return self.df_to_list(list)

    def df_to_list(self,list):
        for index in list:
            self.ticker_list.append(index)
        return self.ticker_list

class Stock_info():
    def __init__(self, ticker, function,api_key):
        self.base_url="https://www.alphavantage.co/query?function={function}{symbol_req}&apikey={api_key}"
        self.results=self.request_url(function,ticker,api_key)

    def format_url(self,function,ticker,api_key):
        return self.base_url.format(function=function,symbol_req=self.function_parse(function,ticker),api_key=api_key)

    def request_url(self,function,ticker,api_key):
        return requests.get(self.format_url(function,ticker,api_key)).json()

    def function_parse(self,function,ticker):
        if self.need_symbol(function):
            symbol="&symbol={ticker}".format(ticker=ticker)
            return symbol
        if not self.need_symbol(function):
            return None

    def need_symbol(self,function):
        """a faire"""
        return True
        
