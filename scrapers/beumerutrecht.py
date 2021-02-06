import requests
import json
import re

from scraper import Scraper
from house import House
from bs4 import BeautifulSoup

class BeumerUtrecht(Scraper):
    url = 'https://beumerutrecht.nl/woningen/'

    def getPossiblePrices(self) -> list[int]:
        return [
            75000,
            100000,
            150000,
            250000,
            350000,
            450000,
            550000,
            650000,
        ]

    def getHouses(self) -> list[House]:
        urls = self.getDetailsUrls()

        houses = []

        for url in urls:
            html = requests.get(url).text

            soup = BeautifulSoup(html, 'html.parser')

            address = soup.find('h1').span.text

            price = soup.find('div', {'class': 'wonen__price'})
            price = self.onlyDigits(price.text)
            
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

    def getDetailsUrls(self):
        min, max = self.getPriceRange()
        
        post_data = {
            '__live': '1',
            '__templates[]': ['search', 'loop'],
            '__maps': 'all',
            'makelaar[]': ['beumermaarssen.nl', 'beumerutrecht.nl', 'beumervleutendemeern.nl', 'beumerwijkbijduurstede.nl'],
            'koophuur': 'koop',
            'plaats_postcode': 'Utrecht',
            'radiuscustom': '',
            'typewoning': '',
            'prijs[min]': str(min),
            'prijs[max]': str(max),
            'status[]':  ['beschikbaar', ''],
            'woningsoort[]': None,
            'liggingen[]': None,
            'buitenruimtes[]': None,
            'bouwperiode[]': None,
            'energielabel[]': None,
            'voorzieningen[]': None,
            'openHuis[]': None,
            'nieuwAanbod[]': None,
            'woonOppervlakte': '',
            'perceelOppervlakte': '',
            'aantalKamers': '',
            'slaapkamers': '',
            'subscribe_email': '',
            'orderby': 'custom_order:asc,publicatiedatum:desc',
        }

        response = requests.post(self.url, data=post_data)

        data = json.loads(response.text)['maps']

        urls = list()
        for entry in data:
            urls.append(self.url + entry['a'])

        return urls