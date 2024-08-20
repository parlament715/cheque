import re
from typing import List,Union
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
class Regex:
    house_variants = ["дом", "д", "корпус", "корп", "строение", "стр", "ш","участок", "уч", "участ", "квартал", "квл", "квртл"]
    street_types = [
        "улица", "ул",
        "проспект", "просп", "пр-кт",
        "пр-д",
        "переулок", "пер",
        "площадь", "пл",
        "шоссе", "ш",
        "бульвар", "бульв", "б-р",
        "набережная", "наб",
        "проезд", "пр", "пр-зд", 
        "аллея", "ал",
        "микрорайон", "мкр", "мкрн",
        "квартал", "кв",
        "дорога", "дор",
        "парк", "парк",
        "сквер", "скв",
        "тупик", "туп",
        "линия", "лин",
        "платформа", "пл",
        "территория", "тер",
        "просека", "просек",
        "зона",
        "учреждение", "учр",
        "курорт", "крт",
        "километр", "км",
        "эстакада", "эст",
        "ряд",
        "переезд", "п-е",
        "колодец", "кол",
        "пост", "пост",
        "тракт", "тр",
        "станция", "ст"
        ]
    @classmethod
    def format_address(cls,address : str) -> str:
        city = cls._take_city(address)
        street = cls._take_street(address)
        house = cls._take_house(address)
        if street is None or house is None or city is None:
            logger.info(f"Regex : {address} -> {city}, {street}, {house}")
            return address # возвращаем тот же адрес
        logger.info(f"Done : {address} -> {city + ", " + street + ", " + house}")
        return city + ", " + street + ", " + house




    @classmethod
    def _take_city(cls, address : str) -> Union[str,None]:
        if re.search(f'(?:Москва)',address):
            return "г. Москва"
        pattern = r"(?:,|\s)(?:город|г|Г)(?:[\.\s]*)([^,\.]*)(?:,|\s)"
        res = re.search(pattern,address)
        if res:
          return res.group().replace(",","").strip()
        else:
          res = re.search(r"[0-9]{1,}\s([а-яА-Я]*)\s",address)
          if res:
            return "г." + res.group().split()[-1].strip()
          return None

    @classmethod
    def _take_house(cls,address : str) -> Union[str,None]:
        variants = cls._variants(cls.house_variants)
        pattern = rf"(?:,|\s)(?:{variants})(?:[\.\s]*)([^,\.]*)(?:,|\b)"
        res = re.search(pattern,address)
        if res:
          res = res.group().replace(",","").strip()
          if re.fullmatch(rf"(?:{variants})",res): ### Если отловил только ул или пр-д то проверяем наоборот например Лихачёва пр-т
            reversed_pattern = fr"(?:,|\s)([^,\.]*)(?:{variants})(?:[\.\s]*)(?:,|\s)"
            reversed_res = re.search(reversed_pattern, address)
            if reversed_res:
              return reversed_res.group().replace(",","").strip()
            return None

          return res
        return None

    @classmethod
    def _take_street(cls,address : str) -> Union[str,None]:
        variants = cls._variants(cls.street_types)
        pattern = fr"(?:,|\s)(?:{variants})(?:[\.\s]*)([^,\.]*)(?:,|\s)"
        res = re.search(pattern,address)

        if res:
          res = res.group().replace(",","").strip()
          if re.fullmatch(rf"(?:{variants})",res): ### Если отловил только ул или пр-д то проверяем наоборот например Лихачёва пр-т
            reversed_pattern = fr"(?:,|\s)([^,\.]*)(?:{variants})(?:[\.\s]*)(?:,|\s)"
            reversed_res = re.search(reversed_pattern, address)
            if reversed_res: # Если он есть
              reversed_res = reversed_res.group().replace(",","").strip()
              if re.fullmatch(rf"(?:{variants})",reversed_res): # если он не нашёл ничего кроме пр-т даже так то -> None
                return None
              return reversed_res
            return None

          return res
        return None

    @classmethod
    def _variants(cls, types : List[str]) -> str:
        return "|".join(types)

