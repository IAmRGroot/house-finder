import os

from abc import ABC, abstractmethod
from house import House

class Scraper(ABC):
    @abstractmethod
    def getHouses(self) -> list[House]:
        pass

    def getPriceRange(self) -> list[(int, int)]:
        prices = self.getPossiblePrices()

        env_min = int(os.getenv('MIN'))
        env_max = int(os.getenv('MAX'))

        minimum = 0
        maximum = 0

        for index, price in enumerate(prices):
            if price < env_min:
                minimum = price
            if price < env_max:
                maximum = prices[min(index + 1, len(prices) - 1)]

        return (minimum, maximum)

    def getPossiblePrices(self) -> list[int]:
        return list()

    def getMinSize(self) -> int:
        sizes = self.getPossibleSizes
        
        env_min = int(os.getenv('MIN_SIZE'))
        min = 0

        for size in sizes:
            if min < env_min:
                min = size

    def getPossibleSizes(self) -> list[int]:
        return list()

    def getDetailsUrls(self) -> list[(str, object)]:
        return list()

    def getHouseFromUrl(self, url: str) -> House:
        pass

    def onlyDigits(self, string: str) -> int:
        return int(''.join(filter(str.isdigit, string)))

    def getName(self):
        return self.__class__.__name__
