from openpyxl import Workbook
from typing import List,Tuple
import os
from icecream import ic

class Excel_db:
    def __enter__(self):
        self.global_letters = ("B","C","D","E","F","G","H","I","J")
        self.row = "2"
        self.global_names = ("Username","Название компании","Дата","Адрес","Чек №","ФД","Смена №","ФД/Смена","Комментарий")
        wb = Workbook()
        self.wb = wb
        self.sheet = wb.active
        self.file_name = 'db.xlsx'

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.path.exists(self.file_name):
            os.remove(self.file_name)
        
        file_path = os.path.join(os.getcwd(), self.file_name)
        print(file_path)
        self.wb.save(file_path)
        

    def _create_header(self):
      for letter,value in zip(self.global_letters,self.global_names):
        self.sheet[letter + self.row] = value

    def _check_on_len(self):
      max_lengths = {}
      for letter,value in zip(self.global_letters,self.global_names): ### дефолтные значения колонок названий
        max_lengths[letter] = len(value)
      for row in self.sheet.iter_rows():
        for cell in row:
          if cell.value:
            cell_len = len(cell.value)
            cell_letter = cell.column_letter
            if cell_letter not in max_lengths:
              max_lengths[cell_letter] = cell_len
            else:
              if cell_len + 2 > max_lengths[cell_letter]:
                max_lengths[cell_letter] = cell_len
      for col_letter, col_len in max_lengths.items():
        self.sheet.column_dimensions[col_letter].width = col_len + 2



    def create_xl(self,res : List[Tuple[str]]):
      self._create_header()
      _letters = ("B","C","D","E","F","G","H","I","J")
      for index,tuuple in enumerate(res):
        listik = list(tuuple)
        last_el = listik.pop(-1)
        fd_del_shift =round(listik[-2]/listik[-1])
        listik.append(fd_del_shift)
        listik.append(last_el)
        index += 3
        letters = []
        for letter in _letters:
          letters.append(letter+str(index))
        for key,value in zip(letters,listik):
          value = str(value)
          self.sheet[key] = value
      self._check_on_len()
