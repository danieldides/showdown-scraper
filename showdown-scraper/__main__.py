import argparse
import asyncio
import csv

import aiohttp
from bs4 import BeautifulSoup


URL = "http://www.showdowncards.com/mlb/mlbsearch.php?a=general&cardnumber=&namecontains=&mascot=&year=01&expansion=&rarity=&storeinfo=&limit=715&limit=0"


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

def parse_header(table):
    headers = table.find('td', {'bgcolor': '#CC0033'}).parent.find_all('td')[1:]
    
    return [header.string for header in headers]



def parse_html(html):
    table = BeautifulSoup(html, 'html.parser').find('table', {'width': '750'})

    headers = parse_header(table)

    data = headers
    
    return data


async def main(loop, config):
    if config.local:
        with open(config.local, 'rb') as infile:
            html = infile.read()
    else:
        async with aiohttp.ClientSession(loop=loop) as session:
            html = await fetch(session, URL)
    
    data = parse_html(html)

    print(data)


def get_config():
    parser = argparse.ArgumentParser(prog="Showdown Scraper", description="Scrape the showdown card site")

    parser.add_argument("--local", dest="local", help="load local file for testing")

    return parser.parse_args()



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    config = get_config()

    loop.run_until_complete(main(loop, config))
