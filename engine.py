import concurrent.futures
import datetime
import math
import time

import pandas as pd
from googleapiclient.discovery import build
from numpy import mod
from requests.models import HTTPError

import config
from credentials import credential
from data import DB
from data.ticker_data import stock_data as sd

api_keys=config.config().api_key

class database_update():
    def __init__(self):
        pass

    def database_iterator(self,request=None,list=None,all_pop=False,period=None,interval=None,begin_date=None,end_date=None):
        msg_log=[]
        for tickers in list:
            msg_log.append(self.database_update(tickers,request,all_pop,period=period,interval=interval,begin_date=begin_date,end_date=end_date))
        return msg_log

    def database_update(self,tickers,request,all_pop,period=None,interval=None,begin_date=None,end_date=None):
        try:
            param = sd(tickers,api_keys,bool_choice=all_pop,period=period,interval=interval,begin_date=begin_date,end_date=end_date).function_mapper[request]
            msg_log=param()
            msg_log=msg_log["msg_log"]    
            return msg_log
        except ValueError as e:
            return f"{e}"

class calendar():
    def __init__(self):
        self.event_to_process=[]
        if not credential.calendar().authenticated:credential.calendar().authorize()
        self.service = build("calendar", "v3", credentials=credential.calendar().creds)
            
    def get_event_list(self):
        event_list=[]
        service = build("calendar", "v3", credentials=credential.calendar().creds)
        events=service.events().list(calendarId="primary").execute()
        for event in events["items"]:
            try:
                event_list.append(event['summary'], event['id'])
            except:pass
        return event_list
    
    def generate_event(self):
        df=self.db_to_df()
        for i in range(len(df.index)):
            row=df.iloc[i]
            args=[row["symbol"],row["dividend_rate_yield"],row["price"],row["pe_ratio"],
            row["earning_date"],row["range_52"],row["beta"],row["dividend_date"]]
            self.event_to_process.append(self.event_parser(args))
        return self.event_to_process

    def create_events(self,event):
        print("creating {event}".format(event=event))
        try:    
            self.service.events().insert(calendarId="primary", body=event).execute()
        except HTTPError as e:
            print(e)

    def event_parser(self, args):
        date = datetime.datetime.strptime(args[7], "%b %d, %Y")
        event = {
    "summary": args[0],
    "description": "Symbol : {s} | Rate : {r}, price : {p}, pe_ratio : {pe}, earning_date : {ed}, range_52 : {rg}, beta : {b}".format(
        s=args[0],r=args[1],p=args[2],pe=args[3],ed=args[4],rg=args[5],b=args[6]),
    "start": {
        "date": "{t}".format(t=date.date()),
        "timeZone": "America/New_York",
    },
    "end": {
        "date": "{t}".format(t=date.date()),
        "timeZone": "America/New_York",
    }
    }
        return event
    def db_to_df(self):
        query="SELECT * FROM stock_data"
        headers=["symbol","date_generated","price","dividend_date","dividend_rate_yield","pe_ratio","earning_date","range_52","beta"]
        results=DB.database().execute_read_query(query)
        df=pd.DataFrame(results,columns=headers)
        return df
    
    def event_iterator(self):
        item_to_process=calendar().generate_event()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_event = {executor.submit(self.create_events,e): e for e in item_to_process}
                for future in concurrent.futures.as_completed(future_event):
                    fe=future_event[future]
                    try:fe=future.result()
                    except:pass
        return fe
    def delete_event(self):
        return self.service.calendars().clear(calendarId='primary').execute()
