import requests
import os

from scraper import Scraper
from house import House
from bs4 import BeautifulSoup

class DeKeizer(Scraper):
    url = 'https://www.dekeizer.nl'

    def getPriceRange(self) -> (int, int):
        return (os.getenv('MIN'), os.getenv('MAX'))

    def getMinSize(self) -> int:
        return os.getenv('MIN_SIZE')

    def getHouses(self) -> list[House]:
        url = self.url + '/0-2ac6/aanbod-pagina'

        min, max = self.getPriceRange()

        data = {
            'forsaleorrent': 'FOR_SALE',
            'iscustom': 'true',
            'isnewstate': 'false',
            'minlivablearea': self.getMinSize(),
            'orderby': '9',
            'pricerange.maxprice': max,
            'pricerange.minprice': min,
            'take': '99',
            'typegroups[0]': '18',
            'minrooms': '0',
        }

        soup = BeautifulSoup(requests.post(url, data=data).text, 'html.parser')
        houses_divs = soup.find_all('div', class_='objectoutercontainer')

        houses = []

        for house_div in houses_divs:
            address = house_div.find('h3').text

            if not ('te koop' in address.lower()):
                continue

            price = self.onlyDigits(house_div.find('span', {'class': 'obj_price'}).text)
            address = address.split(',')[0].split(':')[1]

            size = house_div.find(text='Grootte:')
            size = size.parent.findNext('span').text.split(',')[0]

            link = house_div.find('a')['href'].split('?')[0]

            houses.append(
                House(
                    address=address,
                    link=self.url + link,
                    price=price,
                    size=size
                )
            )

        return houses