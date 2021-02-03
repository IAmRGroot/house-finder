import requests
import json
import os

from scraper import Scraper
from house import House
from bs4 import BeautifulSoup

class Domvast(Scraper):
    def getPriceRange(self) -> (int, int):
        return (os.getenv('MIN'), os.getenv('MAX'))

    def getMinSize(self) -> int:
        return os.getenv('MIN_SIZE')

    def getHtml(self) -> str:
        min, max = self.getPriceRange()

        url = 'https://www.domvast.nl/huizen/smartselect.aspx'
        data = {
            'plaatsnaam': 'Utrecht', 
            'woonopp': str(self.getMinSize()), 
            'sorteer': 'Desc~Datum,Asc~Prijs',
            'prijs': str(min) + ',' + str(max),
            'prefilter': 'Koopaanbod',
            'pagenum': '0',
            'pagerows': '1000',
        }

        response = requests.post(url, data = data)
        result = json.loads(response.text)

        matches = result['AllMatches']

        url = 'https://www.domvast.nl/huizen/smartelement.aspx'
        data = {
            'id': ','.join(matches)
        }

        return requests.post(url, data = data).text

    def getHouses(self) -> list[House]:
        houses = []

        soup = BeautifulSoup(self.getHtml(), 'html.parser')

        objects = soup.findAll('div', {'class': 'object'})

        for house_object in objects:
            address = house_object.find('span', {'class', 'adres'})
            link = house_object.find('a', {'class', 'adreslink'})
            price = house_object.find('span', {'class', 'element_prijs2'})
            
            size = house_object.find(text='Gebruiksoppervlak wonen')

            if size is not None:
                size = size.parent.findNext('div').string

            status = house_object.find('div', {'class', 'status'})

            # Only has status if has bid or is sold
            if status is not None:
                continue

            if price is not None:
                price = price.string

            if link is not None:
                link = link['href']

            houses.append(
                House(
                    address=address.string,
                    link=link,
                    price=price,
                    size=size
                )
            )

        return houses