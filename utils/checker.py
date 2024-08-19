from bs4 import BeautifulSoup
from typing import Union, Dict
from icecream import ic
from utils.parser import Parse
class Checker:

  def __init__ (self,bot):
    self.bot = bot

  async def check_all(self,file_id : str, file_name : str,) -> Dict[str,str]:
    if file_id:
        if file_name.split(".")[-1] == "html":
            await self._download_file(file_id)
            with open("cheques/file.html", encoding='utf-8') as file:
              src = file.read()
            soup = BeautifulSoup(src,"lxml")
            if not self.__checker_on_cheque(soup):
              raise Exception("Это не кассовый чек") 
            ### взять данные
            tds = soup.find("tbody").find_all("td")
            address = self._take_address(tds)
            data = self._take_other_data(tds)
            if address is None:
              coordinates = None
            else:
              coordinates, address = await Parse.parse_coordinates_and_address(address)
            data["address"] = address
            data["coordinates"] = coordinates
            return data

        else:
          raise Exception("Расширение не .html")

    else:
        raise Exception("Нет файла")


  def __checker_on_cheque(self, soup : BeautifulSoup):
    if soup.find("p",class_="versionFFD"):
      return  "КАССОВЫЙ ЧЕК" in str(soup.find("p",class_="versionFFD").text)
    elif soup.find("caption").find_all("li"):
      for elem in soup.find("caption").find_all("li"):
        if "КАССОВЫЙ ЧЕК" in elem.text:
          return True
    return False


  async def _download_file(self,file_id : str) -> None:
    file = await self.bot.get_file(file_id)
    # Укажите папку дл
    await self.bot.download_file(file.file_path,"cheques/file.html")


  def _take_address(self,tds : BeautifulSoup) -> Union[None,str]:
    for td in tds:
      if str(td.text).startswith("Адрес"):
        address =str(td.text).split(":")[1]
        return address.strip()
    return None 

  def _take_other_data(self,tds)->Dict[str, str]:
    data = dict()
    # names = ["Дата","Смена","Чек","ФД №"]
    for td in tds:
      if ":" in str(td.text):
        splitter = ":"
      else:
        splitter = " "
      if str(td.text).startswith("Дата"):
        data["date_time"] = str(td.text).replace(":","@@",1).split("@@")[1].strip()
      elif str(td.text).startswith("Чек"):
        data["cheque_number"] = str(td.text).replace(" №","").split(splitter)[1].strip()
      elif str(td.text).startswith("ФД"):
        data["FD"] = str(td.text).replace(" №","").split(splitter)[1].strip()
      elif str(td.text).startswith("Смена"):
        data["shift_number"] = str(td.text).replace(" №","").split(splitter)[1].strip()
    return data

