import pandas as pd
from typing import List,Tuple
from icecream import ic

class Excel_db:
    file_name = 'db.xlsx'
    @classmethod
    def create_xl(cls,cnx):
      df = pd.read_sql_query("SELECT * FROM cards", cnx)
      df.to_excel(cls.file_name, index=False,startcol=1, startrow=1)
