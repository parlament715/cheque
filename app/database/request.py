import sqlite3
from icecream import ic
from typing import Union, Optional, Tuple



class Request():

    def __init__(self):
        conn = sqlite3.connect('request.db')

        cursor = conn.cursor()

        cursor.execute(f'''CREATE TABLE IF NOT EXISTS "users"
                        (id_telegram INTEGER PRIMARY KEY NOT NULL,
                        user_name_telegram TEXT,
                        is_subscribed BOOLEAN,
                        balance INTEGER,
                        wallet TEXT,
                        datetime_registration TEXT
                        )
                        ''')
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS "refers" 
                        (id INTEGER,
                        id_refers INTEGER PRIMARY KEY NOT NULL
                        )
        ''')
        self.conn = conn
        self.cursor = cursor

    def con_close(self):
        self.conn.close()
    
    def select_one(self, table : str, column :str, where : str = None) -> Tuple:
        if where != None:
            res = self.cursor.execute(
                f'''
                SELECT "{column}" FROM "{table}" WHERE {where}
                '''
            ).fetchone()
        
        else:
            res = self.cursor.execute(
                    f'''
                    SELECT "{column}" FROM "{table}"
                    '''
                ).fetchone()
        
        return res

    def select_many(self,table : str,column :str,where : str = None) -> Tuple:
        if where != None:
            res = self.cursor.execute(
                f'''
                SELECT "{column}" FROM "{table}" WHERE {where}
                '''
            ).fetchall()
        
        res = self.cursor.execute(
                f'''
                SELECT "{column}" FROM "{table}"
                '''
            ).fetchall()
        return res

    def write_insert(self,table_name : str,columns_and_values : list) -> None:
        columns = ""
        values = ""
        for column,value in columns_and_values:
            column,value = str(column),str(value)
            columns += column + ", "
            values += value + ", "
        self.cursor.execute(f'''INSERT INTO {table_name} ({columns[:-2]}) VALUES ({values[:-2]})''')
        self.conn.commit()
        
    def write_update(self,table_name : str,columns_and_values : list, where : str = None) -> None:
        columns = ""
        values = ""
        for column,value in columns_and_values:
            column,value =str(column),str(value)
            columns += column + ","
            values += value + ","
        if where == None:
            self.cursor.execute(f'''UPDATE "{table_name}" SET ({columns[:-1]}) ({values[:-1]})''')
        else:
            ic(f'''UPDATE "{table_name}" SET ({columns[:-1]}) = 
            ({values[:-1]}) WHERE {where}''')
            self.cursor.execute(f'''UPDATE "{table_name}" SET ({columns[:-1]}) = 
            ({values[:-1]}) WHERE {where}''')
        self.conn.commit()
    