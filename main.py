
import time
import requests
import os
import json

from datetime import datetime
from dotenv import load_dotenv
from tinydb import TinyDB, where

from scrapers.domvast import Domvast
from scrapers.beumerutrecht import BeumerUtrecht
from scrapers.rvl import RVL
from scrapers.molenbeek import Molenbeek
from scrapers.makelaar1 import Makelaar1
from scrapers.lauteslager import Lauteslager
from scrapers.punt import Punt
from scrapers.debree import DeBree

from scrapers.realworks import createRealworksInstances

def notify(message: str) -> bool:
    url = 'https://api.telegram.org/bot' + os.getenv('TELEGRAM_API_KEY') + '/sendMessage'
    data = {
        'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
        'text': message,
        'parse_mode': 'MarkdownV2'
    }

    try:
        response = requests.post(url, data = data)
        result = json.loads(response.text)['ok']
    except Exception as e:
        print('Notify failed D:')
        print(e)

    if not result:
        print('Notify failed D:')
        print(response.text)

    return result

def search():
    print('')

    sources = [
        Domvast(),
        BeumerUtrecht(),
        RVL(),
        Molenbeek(),
        Makelaar1(),
        Lauteslager(),
        Punt(),
        DeBree(),
    ]

    sources.extend(createRealworksInstances())

    ip_response = requests.get('https://ifconfig.me')

    message = 'Searching the interwebs at ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ' with IP: ' + ip_response.text

    print(message)
    notify(message.replace('.', '\\.'))

    db = TinyDB('db.json')

    for source in sources:
        try:
            print('Searching in ' + source.getName())

            new_houses = source.getHouses()

            if len(new_houses) == 0:
                print('    No houses found :(')

            for house in new_houses:
                if house.address is None:
                    print('    House parsing failed!')
                    notify('    House parsing failed!')
                    continue

                if db.contains(where('address') == house.address):
                    print('    Found existing house: ' + house.address)
                else:
                    print('    Found new house: ' + house.address)
                    db.insert({'address': house.address})
                    notify(house.toMarkdown())
        except Exception as e:
            print('    ' + str(e))
            notify('Error in housefinder at source: ' + source.getName())

    print('Done for now :D')
    print('')

if __name__ == '__main__':
    load_dotenv()

    search()
