if __name__ != "__main__":
    from utils.regex import Regex
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from typing import Tuple
import asyncio
from icecream import ic
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# настройка обработчика и форматировщика для logger2
handler = logging.FileHandler(f"log/{__name__}.log", mode='w', encoding = "UTF-8")
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
# добавление форматировщика к обработчику
handler.setFormatter(formatter)
# добавление обработчика к логгеру
logger.addHandler(handler)


class Parse:
    _base_url = "https://yandex.ru/maps/213/moscow/?ll=37.734853%2C55.714044&z=10.07"
    _options = webdriver.ChromeOptions()
    _options.add_argument('log-level=3')

    _options.add_argument("--disable-blink-features=AutomationControlled")
    _options.add_argument("--headless")
    _browser = webdriver.Chrome(options=_options)
    logger.info("Browser is open")
    

    @classmethod
    async def parse_coordinates_and_address(cls, address : str) -> Tuple[Tuple[str,str],str]:
        if address == None:
          return None, None
        logger.info(address)
        cls._browser.get(cls._base_url)
        logger.info("Getting page ...")
        await asyncio.sleep(0.4)
        search_box=cls._browser.find_element("class name", "input__control")
        address = Regex.format_address(address)
        logger.info(f"After regex : {address}")
        search_box.send_keys(address)
        search_box.send_keys(Keys.ENTER)
        logger.info("Searching ...")
        while True:
            await asyncio.sleep(0.25)
            try :
                cls._browser.find_element("class name", "spinner-view_small__circle")
            except:
                break
        await asyncio.sleep(0.25)
        html = cls._browser.page_source
        soup = BeautifulSoup(html,"html.parser")
        right_address = soup.find("div",class_ = "toponym-card-title-view__description")
        if right_address:
          coordinates = soup.find("div",class_ = "toponym-card-title-view__coords-badge")
          logger.info("Done")
          return coordinates.text,right_address.text
        else:
          logger.info("Error")
          return None, address



async def main():
    ic(await Parse.parse_coordinates_and_address('115193,РОССИЯ,77,город федерального значения Москва,муниципальный округ Даниловский вн.тер.г., Лихачёва пр-кт, д. 16,к. 1, помещение 1Н'))

if __name__ == "__main__":
    from regex import Regex
    asyncio.run(main())