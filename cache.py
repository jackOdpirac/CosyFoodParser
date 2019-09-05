from menu_parsers import MenuParsers
import datetime
from threading import Lock
from typing import List, Tuple

class Cache:
    def __init__(self):
        self._cache = {}
        self._parsers = MenuParsers()
        self._lock = Lock()
        self._parsers = MenuParsers()

    def update(self):
        date = datetime.date.today()

        new_data = {
            "marjetica": self._parsers.marjetica_tobacna(date),
            "viabona": self._parsers.via_bona(date),
            "loncekkuhaj": self._parsers.loncek_kuhaj(date),
                # "kondor": self._parsers.kondor(date),
            "dijaskidom": self._parsers.dijaski_dom_vic(date),
                # "barjan": self._parsers.barjan(date),
            "fe": self._parsers.delicije_fe(date),
            "kurjitat": self._parsers.kurji_tat(date),
            "spar": self._parsers.interspar_vic(date)
                # "ijs": self._parsers.marende_dulcis_ijs(date),
        }

        with self._lock:
            self._cache = new_data

    def contains(self, key : str) -> bool:
        with self._lock:
            return key in self._cache

    def get(self, restaurant : str) -> List[str]:
        with self._lock:
            return self._cache[restaurant]

    def get(self) -> Tuple[List[str]]:
        with self._lock:
            return tuple(self._cache.values())
