import re
from typing import List,Union
from icecream import ic
import logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler(f"log/{__name__}.log", mode='w', encoding = "UTF-8")
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
class Regex:
    house_variants = [
        "дом", "д", "корпус", "корп", "строение", "стр", "ш",
        "участок", "уч", "участ", "квартал", "квл", "квртл"
    ]
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
    def format_address(cls, address: str) -> str:
        """Format a raw address string into a standardized format."""
        city = cls._take_city(address)
        street = cls._take_street(address)
        house = cls._take_house(address)

        if any(value is None for value in [city, street, house]):
            logger.info(f"Error : {address} - > {city}, {street}, {house}")
            return address
        logger.info(f"Done : {address} - > {city}, {street}, {house}")
        return f"{city}, {street}, {house}"

    @classmethod
    def _take_city(cls, address: str) -> Union[str, None]:
        if "Москва" in address:
            return "г. Москва"

        pattern = r",\s*(город|г|Г)\s*([^,]*),*"
        match = re.search(pattern, address)
        if match:
            return match.group(2).strip()

        match = re.search(r"\d+\s*([а-яА-Я]*)\s*", address)
        if match:
            return f"г. {match.group(1).strip()}"

        return None

    @classmethod
    def _take_house(cls, address: str) -> Union[str, None]:
        variants = cls._variants(cls.house_variants)
        pattern = fr",\s*({variants})\s*([^,]*),*"
        match = re.search(pattern, address)
        if match:
            house = match.group(2).strip()
            if re.fullmatch(rf"({variants})", house):
                reversed_pattern = fr",\s*([^,]*)\s*({variants}),*"
                reversed_match = re.search(reversed_pattern, address)
                if reversed_match:
                    return reversed_match.group(1).strip()
                return None
            return house
        return None

    @classmethod
    def _take_street(cls, address: str) -> Union[str, None]:
        variants = cls._variants(cls.street_types)
        pattern = fr",\s*({variants})\s*([^,]*),*"
        match = re.search(pattern, address)
        if match:
            street = match.group(2).strip()
            if re.fullmatch(rf"({variants})", street):
                reversed_pattern = fr",\s*([^,]*)\s*({variants}),*"
                reversed_match = re.search(reversed_pattern, address)
                if reversed_match and not re.fullmatch(rf"({variants})", reversed_match.group(1).strip()):
                    return reversed_match.group(1).strip()
                return None
            return street
        return None

    @classmethod
    def _variants(cls, types: List[str]) -> str:
        return "|".join(types)
    


