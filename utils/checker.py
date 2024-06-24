from bs4 import BeautifulSoup
from typing import Union, Dict
from icecream import ic
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
            ##### взять данные
            tds = soup.find("tbody").find_all("td")
            address = self._take_address(tds)
            data = self._take_other_data(tds)
            data["Адрес"] = address
            return data

        else:
          raise Exception("Расширение не .html")

    else:
        raise Exception("Нет файла")


  def __checker_on_cheque(self, soup : BeautifulSoup):
    if soup.find("p",class_="versionFFD"):
      return  "КАССОВЫЙ ЧЕК" in str(soup.find("p",class_="versionFFD").text)
    return False


  async def _download_file(self,file_id : str) -> None:
    file = await self.bot.get_file(file_id)
    # Укажите папку дл
    await self.bot.download_file(file.file_path,"cheques/file.html")


  def _take_address(self,tds : BeautifulSoup) -> Union[None,str]:
    for td in tds:
      ic(str(td.text))
      if str(td.text).startswith("Адрес расчетов:"):
        address =str(td.text).split(":")[1]
        if address[0].isalnum:
          address = " ".join(address.split()[1:])
        if "федерального значения " in address:
          address = address.replace("федерального значения ","",1)
        if "муниципальный округ " in address:
          address = address.replace("муниципальный округ ","",1)
        return address.strip()
    return None

  # def _take_streets(self,address : str) -> str:
  #   if address.count(",") <= 2:
  #     return None
  #   flag = False
  #   for item in reversed(address.split(",")):
  #     ic(item)
  #     if flag:
  #       return item.strip()
  #     if item.strip().startswith("д.") or item.strip().startswith("ш."):
  #       flag = True
  #     if "ул." in item or "пр-кт" in item or "пр-д" in item:
  #       return item.strip()
  def _take_other_data(self,tds)->Dict[str, str]:
    data = dict()
    names = ["Дата","Смена","Чек","ФД №"]
    for td in tds:
      for name in names:
        if str(td.text).startswith(name):
          if name not in ["ФД №","Дата"]:
            listik = str(td.text).split(":") 
          elif name == "ФД №": ### name ==  "ФД №"
            listik = str(td.text).replace(" №","").split()
          elif name == "Дата":
            listik = str(td.text).replace(":","@@",1).split("@@")
          data[listik[0]] = listik[1].strip()
    return data

