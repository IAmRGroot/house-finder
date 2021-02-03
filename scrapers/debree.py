import requests
import os

from scraper import Scraper
from house import House
from bs4 import BeautifulSoup

class DeBree(Scraper):
    url = 'https://www.debreemakelaars.nl'

    def getPriceRange(self) -> (int, int):
        return int(os.getenv('MIN')), int(os.getenv('MAX'))

    def getMinSize(self) -> int:
        return int(os.getenv('MIN_SIZE'))

    def getHouses(self) -> list[House]:
        houses = []

        page = 1
        response = requests.get(self.url + '/aanbod/page/' + str(page))
        
        while response.status_code == 200:
            houses.extend(self.getHouse(response))

            page += 1
            response = requests.get(self.url + '/aanbod/page/' + str(page))
        
        return houses

    def getHouse(self, response) -> list[House]:
        houses = []

        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        house_divs = soup.find_all('div', class_='grid3column')

        min, max = self.getPriceRange()

        for house_div in house_divs:
            info_divs = house_div.find('div', class_='property-highlight').findChildren('div')

            status = info_divs[1].text.lower()

            if status is not None and ('verkocht' in status or 'onder bod' in status or 'te huur' in status):
                continue

            address_div = house_div.find('div', class_='property-information-address')

            info_div = house_div.find('div', class_='property-highlight').findChildren('div')

            price = self.onlyDigits(info_div[0].text)
            size = str(self.onlyDigits(info_divs[2].text))[:-1]

            if min > price or max < price:
                continue

            link_a = house_div.find('a')

            houses.append(
                House(
                    address=address_div.text.split(',')[0],
                    link=link_a['href'],
                    price=price,
                    size=size,
                )
            )

        return houses
