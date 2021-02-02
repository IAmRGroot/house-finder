import requests
import json

from scraper import Scraper
from house import House
from bs4 import BeautifulSoup

class Domvast(Scraper):
    def getHouses(self) -> list[House]:
        houses = []

        soup = BeautifulSoup(self.getHTML(), 'html.parser')

        objects = soup.findAll('div', {'class': 'object'})

        for house_object in objects:
            address = house_object.find('span', {'class', 'adres'})
            city = house_object.find('span', {'class', 'plaatsnaam'})
            link = house_object.find('a', {'class', 'adreslink'})
            price = house_object.find('span', {'class', 'element_prijs2'})
            
            size = house_object.find(text='Gebruiksoppervlak wonen')

            if size is not None:
                size = size.parent.findNext('div').string

            status = house_object.find('div', {'class', 'status'})

            # Only has status if has bid or is sold
            if status is not None:
                continue

            if city is None or city.string.strip() != 'Utrecht':
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
    
    def getIDs(self) -> list[str]:
        url = 'https://www.domvast.nl/huizen/smartselect.aspx'
        data = {
            'sorteer': 'Desc~Datum,Asc~Prijs',
            'prijs': str(150000) + ',' + str(330000),
            'prefilter': 'Koopaanbod',
            'pagenum': '0',
            'pagerows': '1000',
        }

        response = requests.post(url, data = data)
        result = json.loads(response.text)

        return result['AllMatches']

    def getHTML(self) -> str:
        url = 'https://www.domvast.nl/huizen/smartelement.aspx'
        data = {
            'id': ','.join(self.getIDs())
        }

        response = requests.post(url, data = data)
        
        return response.text