import sqlite3
from icecream import ic
from typing import Union, Optional, Tuple, List, Any



class Request():

    def __init__(self,path):
        self.path = path
        conn = sqlite3.connect(path)

        cursor = conn.cursor()

        cursor.execute(f'''CREATE TABLE IF NOT EXISTS "cards"
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_telegram INTEGER NOT NULL,
                        user_name_telegram TEXT NOT NULL,
                        company_name TEXT NOT NULL,
                        date_time TEXT NOT NULL,
                        address TEXT NOT NULL,
                        cheque_number INTEGER NOT NULL,
                        FD INTEGER NOT NULL,
                        shift_number INTEGER NOT NULL,
                        coordinates TEXT,
                        status INTEGER NOT NULL,
                        comment TEXT 
                        )
                        ''')
        conn.close()

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        return self.cursor
    
    def __exit__(self,exc_type,exc_val,exc_tb):
        self.conn.close()

    def select_one(self, table : str, columns : List[str], where : str = None) -> Tuple:
        if len(columns) == 1 and columns[0].startswith("@"):
            str_columns = columns[0].replace("@","") ### чтобы * не оборачивалась в кавычки "*"
        else:
            str_columns = ''
            for column in columns:
                str_columns += '"' + column + '" ,'
            str_columns = str_columns[:-2]
        if where != None:
            request = (
                f'''
                SELECT {str_columns} FROM "{table}" WHERE {where}
                '''
            )
        
        else:
            request = (
                    f'''
                    SELECT {str_columns} FROM "{table}"
                    '''
                )
        res = self.cursor.execute(request).fetchone()
        return res

    def select_many(self,table : str,columns : List[str],where : str = None) -> Tuple:
        if len(columns) == 1 and columns[0].startswith("@"):
            str_columns = columns[0].replace("@","") ### чтобы * не оборачивалась в кавычки "*"
        else:
            str_columns = ''
            for column in columns:
                str_columns += column + ', '
            str_columns = str_columns[:-2]
        if where != None:
            request = (
                f'''
                SELECT {str_columns} FROM "{table}" WHERE {where}
                '''
            )
        
        else:
            request = (
                    f'''
                    SELECT {str_columns} FROM "{table}"
                    '''
                )
        res = self.cursor.execute(request).fetchall()
        return res

    def write_insert(self,table_name : str, columns_and_values : List[Tuple[str,Any]]) -> None:
        columns = ""
        values = ""
        for column,value in columns_and_values:
            column,value = str(column),str(value)
            columns += column + ", "
            if type(value) == str:
                value = '"' + value + '"'
            values += value + ", "
        self.cursor.execute(f'''INSERT INTO {table_name} ({columns[:-2]}) VALUES ({values[:-2]})''')
        self.conn.commit()
        
    def write_update(self,table_name : str, columns_and_values : List[Tuple[str,Any]], where : str = None) -> None:
        columns = ""
        values = ""
        for column,value in columns_and_values:
            column,value =str(column),str(value)
            columns += column + ", "
            if type(value) == str:
                value = '"' + value + '"'
            values += value + ", "
        if where == None:
            self.cursor.execute(f'''UPDATE {table_name} SET ("{columns[:-2]}") ({values[:-2]})''')
        else:### переделать не работает больше одного параметра за раз
            self.cursor.execute(f'''UPDATE {table_name} SET ("{columns[:-2]}") = ({values[:-2]}) WHERE {where}''')
        self.conn.commit()
    