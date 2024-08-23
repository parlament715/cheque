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
        html = requests.get(f'https://yandex.ru/maps?text={address}').text
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
    # while True:
        ic(await Parse.parse_coordinates_and_address('- город Москва, вн.тер.г. Зюзино,117638, ул Одесская, д. 2'))

if __name__ == "__main__":
    from regex import Regex
    asyncio.run(main())