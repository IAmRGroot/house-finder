import requests
import os

from scraper import Scraper
from house import House
from bs4 import BeautifulSoup

class RVL(Scraper):
    def getPriceRange(self) -> (int, int):
        return (os.getenv('MIN'), os.getenv('MAX'))

    def getMinSize(self) -> int:
        return os.getenv('MIN_SIZE')

    def getHouses(self) -> list[House]:
        houses = []

        for url in self.getDetailsUrls():
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')

            address = str.strip(soup.find('h3').text.split('\n')[1])
            size    = soup.find('span', {'class': 'size'}).text.split('m')[0]
            price   = self.onlyDigits(soup.find('span', {'class': 'rate'}).text)

            houses.append(House(
                address=address,
                link=url,
                price=price,
                size=size
            ))

        return houses

    def getDetailsUrls(self) -> list[(str, object)]:
        min, max = self.getPriceRange()

        html = requests.get('https://www.rvlmakelaars.nl/koopwoningen-utrecht?a=Utrecht&m=' + min + '&e=' + max + '&sb=latest').text

        soup = BeautifulSoup(html, 'html.parser')
        container = soup.find('div', {'class': 'homeBox'}).div

        urls = []

        for house_div in container.findChildren('div'):
            if not house_div.has_attr('data-object'):
                continue

            urls.append(house_div.a['href'])

        return urls
