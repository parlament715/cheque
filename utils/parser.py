if __name__ != "__main__":
    from utils.regex import Regex
import time
from bs4 import BeautifulSoup
from typing import Tuple
import asyncio
from icecream import ic
import logging
import requests 

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
    @classmethod
    async def parse_coordinates_and_address(cls, address : str) -> Tuple[Tuple[str,str],str]:
        if address == None:
            return None, None
        address = Regex.format_address(address)
        logger.info("Произвожу запрос к yandex.ru")
        response = requests.get(f'https://yandex.ru/maps?text={address}')
        url = None
        html = response.text
        # with open("file.html", "w", encoding='utf-8') as file:
        #     file.write(html)
        soup = BeautifulSoup(html,"html.parser")
        services = None
        try:
            a_obzor = soup.find("a",class_ = "tabs-select-view__label")
            if a_obzor:
                if a_obzor.text == "Обзор":
                    logger.info("Нашёл house в обзоре")
                    url = a_obzor["href"]
                else:
                    logger.warning("Не найдено обзора error 1: " + address, " a_obzor.text = ",a_obzor.text)
                    return None, address
            else:
                logger.warning("Не найдено обзора error 2 возможно каптча: " + address)
                return None, address
            
        except:
            logger.warning("Не найдено обзора error 3: " + address)
            return None, address
        ic(url)
        if "house" in url:
            right_address = soup.find("div",class_ = "toponym-card-title-view__description")
            if right_address:
                coordinates = soup.find("div",class_ = "toponym-card-title-view__coords-badge")
                logger.info(f"+++ {address} -> {right_address.text} ")
                return coordinates.text,right_address.text
            else:
                logger.warning("Error : " + address)
                return None, address
        logger.warning("Не нашлось house in url : " + address)
        return None, address



async def main():
    # while True:
        ic(await Parse.parse_coordinates_and_address('Варшавское шоссе, 170Ек5, Москва, 117405'))

if __name__ == "__main__":
    from regex import Regex
    asyncio.run(main())