import requests
import os

from scraper import Scraper
from house import House
from bs4 import BeautifulSoup

def createRealworksInstances() -> list[Scraper]:
    instances = []

    with open('realworks_sites.txt', 'r') as file:
        for line in file:
            split = line.split()
            instances.append(Realworks(name=split[0], url=split[1]))

    return instances

class Realworks(Scraper):
    def __init__(self, name: str, url: str):
        self.url = url
        self.name = name
        
        min, max = self.getPriceRange()
        self.min = str(min)
        self.max = str(max)

        self.size = self.getMinSize()

    def getMinSize(self) -> int:
        return os.getenv('MIN_SIZE')

    def getPossiblePrices(self) -> list[int]:
        return [
            75000,
            100000,
            125000,
            150000,
            175000,
            200000,
            225000,
            250000,
            275000,
            300000,
            325000,
            350000,
            375000,
            400000,
            450000,
            500000,
        ]

    def getName(self):
        return self.name

    def getHouses(self) -> list[House]:
        if self.url is None:
            raise Exception('URL not given value')

        houses = []

        html = requests.get(self.url + '/aanbod/woningaanbod/UTRECHT/+5km/' + self.size + '+woonopp/' + self.min + '-' + self.max + '/koop/aantal-80/').text

        soup = BeautifulSoup(html, 'html.parser')

        house_lis = soup.find_all('li', class_='aanbodEntry')

        for house_li in house_lis:
            status = house_li.find('span', class_='objectstatusbanner').text.lower()

            if 'verkocht' in status or 'onder bod' in status:
                continue

            address_span = house_li.find('h3', {'class': 'street-address'})

            price_span = house_li.find('span', class_='koopprijs')
            price_span = price_span.find('span', class_='kenmerkValue')

            size_span = house_li.find('span', class_='woonoppervlakte')

            size_text = '?'

            if size_span is not None:
                size_span = size_span.find('span', class_='kenmerkValue')
                size_text = size_span.string.split()[0]

            link_a = house_li.find('a', class_='aanbodEntryLink')

            houses.append(
                House(
                    address=address_span.string,
                    link=self.url + link_a['href'],
                    price=self.onlyDigits(price_span.string),
                    size=size_text
                )
            )

        return houses

