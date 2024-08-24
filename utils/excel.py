import pandas as pd
from typing import List,Tuple
from icecream import ic
import openpyxl

class Excel_db:
    file_name = 'db.xlsx'
    @classmethod
    def create_xl(cls,cnx):
        df = pd.read_sql_query("SELECT * FROM cards", cnx)
        df.to_excel(cls.file_name, index=False,startcol=1, startrow=1)
        cls._change_width()
    
    @classmethod
    def _change_width(cls):
        wb = openpyxl.load_workbook(cls.file_name)
        sheet = wb.active

        for col_idx in range(1, sheet.max_column + 1):
            max_length = 0
            for cell in sheet.iter_cols(min_col=col_idx, max_col=col_idx):
                for cell_obj in cell:
                    if len(str(cell_obj.value)) > max_length:
                        max_length = len(str(cell_obj.value))
            sheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = max_length + 2

            # Выравнивание колонки по тексту
            for cell in sheet.iter_cols(min_col=col_idx, max_col=col_idx):
                for cell_obj in cell:
                    cell_obj.alignment = openpyxl.styles.Alignment(horizontal='left')

        wb.save(cls.file_name)

# if __name__ == "__main__":
#     import sqlite3
#     cnx = sqlite3.connect("request.db")
#     Excel_db().create_xl(cnx)