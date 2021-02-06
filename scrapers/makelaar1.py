import requests
import re
import os

from scraper import Scraper
from house import House
from bs4 import BeautifulSoup

class Makelaar1(Scraper):
    def getPriceRange(self) -> (int, int):
        return (os.getenv('MIN'), os.getenv('MAX'))

    def getMinSize(self) -> int:
        return os.getenv('MIN_SIZE')

    def getMainUrl(self) -> str:
        min, max = self.getPriceRange()
        size = self.getMinSize()

        return 'https://www.makelaar1.nl/?minvraagprijs=' + min + '&maxvraagprijs=' + max + '&plaats=utrecht&straalkm=10&typeobject=koop&keuze=zoeken&woonopp=' + size

    def getHouses(self) -> list[House]:
        houses = []

        html = requests.get(self.getMainUrl()).text

        soup = BeautifulSoup(html, 'html.parser')

        page_select = soup.find('select', {'class': 'submitZoeken'})

        last_page = None
        for option in page_select.find_all('option'):
            last_page = option

        for page in range(1, int(last_page['value']) + 1):
            html = requests.get(self.getMainUrl() + '&page2=' + str(page)).text

            soup = BeautifulSoup(html, 'html.parser')

            for house_div in soup.find_all('div', class_='object'):
                status_div = house_div.find('div', class_='statusLabel')

                if status_div is not None: 
                    continue

                address_div = house_div.find('div', class_='objectKop')
                price_div = house_div.find('div', class_='objectPrice')
                link_div = house_div.find('div', class_='objectThumbs')
                size_div = house_div.find(text=re.compile('Woonopp.*'))

                houses.append(
                    House(
                        address=address_div.text,
                        link=link_div.a['href'].split('?')[0],
                        price=self.onlyDigits(price_div.text.strip()),
                        size=size_div[9:].split()[0]
                    )
                )

        return houses
