import sqlite3 as sql
from sqlite3 import Error
import os

from pandas.core.frame import DataFrame
path= os.path.join("data","database.db")

class database():
    def __init__(self):
        #print(index)
        #table_query=self.create_table(function,index)
        self.conn=self.connection(path)
        
    def connection(self, path):
        try :
            self.conn = sql.connect(path)
            print("Connection Successful")
            return self.conn
        except Error as e:
            return f"The error {e} has occured"
        

    def execute_read_query(self,query):
        result=None
        try:
            self.conn.execute(query)
            result=self.conn.cursor().fetchall()
            return result
        except Error as e:
            return f"The error {e} has occured"
        
    def query_executor(self,table,values,type,key):
        """
        can use "INSERT" or "UPDATE"
        key take the symbol of the query to
        values is the dataframe
        """
        formatted_query=self.query_builder(table,values,key,type="INSERT")
        try:
            self.conn.execute(formatted_query)
            self.conn.commit()
            
            return f"Query Executed Successfully For {key}"
        except Error as e:
            return f"The Error {e} Has Occured For {key}"

    def index_parser(self, index):
        return str(index).strip("[").strip("]")

    def query_builder(self,values:DataFrame,key:dict,type:str,table:str):
        k=key.keys()
        v=key.get(k)
        formatted_value=values.to_dict("dict")
        string=[]
        for k in formatted_value.keys():
            s=f"{k} = {formatted_value[k]}"
            string.append(s)
        print(string)
        query=f"""
        {type} {table}
                SET {formatted_value}
                WHERE {key_name} = '{key}'
        """

        
