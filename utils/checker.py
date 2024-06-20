from bs4 import BeautifulSoup
from typing import Union
from icecream import ic
class Checker:

  def __init__ (self,bot):
    self.bot = bot

  async def check_all(self,file_id : str, file_name : str,) -> Union[str, None]:
    if file_id:

        if file_name.split(".")[-1] == "html":
            await self._download_file(file_id)
            with open("cheques/file.html", encoding='utf-8') as file:
              src = file.read()
            soup = BeautifulSoup(src,"lxml")
            if not self.__checker_on_cheque(soup):
               return "Это не кассовый чек"
            address = self._take_address(soup)
            if address is None:
              return "Здесь нет адреса"
            else:
              return address

        else:
          return "Расширение не .html"

    else:
        return "Нет файла"
      
  def __checker_on_cheque(self, soup : BeautifulSoup):
    if soup.find("p",class_="versionFFD"):
      return  "КАССОВЫЙ ЧЕК" in str(soup.find("p",class_="versionFFD").text)
    return False


  async def _download_file(self,file_id : str) -> None:
    file = await self.bot.get_file(file_id)
    # Укажите папку дл
    await self.bot.download_file(file.file_path,"cheques/file.html")

  def _take_address(self,soup : BeautifulSoup) -> Union[None,str]:
    tds = soup.find("tbody").find_all("td")
    for td in tds:
      ic(str(td.text))
      if str(td.text).startswith("Адрес расчетов:"):
        address =str(td.text).split(":")[1]
        street = self._take_streets(address)
        ic(street)
        if not street:
          return f"Не удалось найти улицу в адресе {address}"
        return street
    return None
  def _take_streets(self,address : str) -> str:
    if address.count(",") <= 2:
      return None
    flag = False
    for item in reversed(address.split(",")):
      ic(item)
      if flag:
        return item
      if item.strip().startswith("д.") or item.strip().startswith("ш."):
        flag = True
      if "ул." in item or "пр-кт" in item or "пр-д" in item:
        return item

