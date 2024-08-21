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
    _options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
    _options.add_argument("--disable-blink-features=AutomationControlled")
    _options.add_argument("--headless")
    _options.add_argument("--no-sandbox")
    _browser = webdriver.Chrome(options=_options)
    logger.info("Browser is open")
    

    @classmethod
    async def parse_coordinates_and_address(cls, address : str) -> Tuple[Tuple[str,str],str]:
        if address == None:
            return None, None
        logger.info(address)
        cls._browser.get(cls._base_url)
        logger.info("Getting page ...")
        await asyncio.sleep(0.25)
        try:
            search_box=cls._browser.find_element("class name", "input__control")
        except:
            logging.warning("Captcha")
            await asyncio.sleep(1)
            html = cls._browser.page_source
            with open('page.html', 'w',encoding="UTF-8") as fp:
                fp.write(html)
            return None, "Captcha"
        if search_box is None:
            # await asyncio.sleep(200)
            return None, address
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
        await asyncio.sleep(0.4)
        html = cls._browser.page_source
        soup = BeautifulSoup(html,"html.parser")
        organizations = None
        try:
            organizations = soup.find("div",class_ = "tabs-select-view__title _name_inside")
        except:
            ic("Не нашлось организаций")
            return None, address
        if organizations:
            right_address = soup.find("div",class_ = "toponym-card-title-view__description")
            if right_address:
                coordinates = soup.find("div",class_ = "toponym-card-title-view__coords-badge")
                logger.info(f"+++ {address} -> {right_address.text} ")
                return coordinates.text,right_address.text
            else:
                logger.warning("Error : " + address)
                return None, address
        return None, address



async def main():
    while True:
        ic(await Parse.parse_coordinates_and_address('Москва 4-я Тверская-Ямская 27'))

if __name__ == "__main__":
    from regex import Regex
    asyncio.run(main())