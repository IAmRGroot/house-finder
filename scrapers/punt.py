import requests
import os

from scraper import Scraper
from house import House
from bs4 import BeautifulSoup

class Punt(Scraper):
    url = 'https://puntmakelaars.nl'

    def getPriceRange(self) -> (int, int):
        return (os.getenv('MIN'), os.getenv('MAX'))

    def getMinSize(self) -> int:
        return int(os.getenv('MIN_SIZE'))

    def getMainUrl(self) -> str:
        min, max = self.getPriceRange()
        size = self.getMinSize()

        return self.url + '/nl/aanbod/?q=&woonoppervlakte=' + str(size) + '&prijs=' + min + '-' + max

    def getDetailsUrls(self) -> list[str]:
        html = requests.get(self.getMainUrl()).text
        
        soup = BeautifulSoup(html, 'html.parser')

        house_ul = soup.find('ul', class_='listHouses')
        house_lis = house_ul.find_all('li')

        urls = []

        for house_li in house_lis:
            if house_li.get('id') is not None:
                continue

            status_span = house_li.find('span', class_='houseOverviewStatus')
            if status_span is not None:
                status = house_li.find('span', class_='houseOverviewStatus').text.lower()

            if status_span is not None and ('verkocht' in status or 'onder bod' in status):
                continue

            address_span = house_li.find('span', {'class': 'houseOverviewStreet'})
            price_span = house_li.find('span', class_='houseOverviewPrice')

            link = house_li.find('a')['href']

            urls.append(self.url + link)

        return urls

    def getHouses(self) -> list[House]:
        houses = []

        for url in self.getDetailsUrls():
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')

            address = soup.find('h1').text.split('|')[1].strip()

            price = self.onlyDigits(soup.find('h2').text)

            size = soup.find(text='Woonoppervlakte')
            size = size.find_next('td').text.split()[0]

            houses.append(
                House(
                    address=address,
                    link=url,
                    price=price,
                    size=size
                )
            )

        return houses