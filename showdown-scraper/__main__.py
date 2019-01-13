import argparse
import asyncio
import csv
import datetime
import itertools
import math

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Tag

from .constants import Row, PLAYER_DICT


URL = "http://www.showdowncards.com/mlb/mlbsearch.php?a=general&cardnumber=&namecontains=&mascot=&year=01&expansion=&rarity=&storeinfo=&limit=715&limit={numbers}"

# "Your search returned 740 results on 30 pages with 25 results per page.'
NUM_PAGES = math.ceil(740 / 25)
PER_PAGE = 25


async def fetch(session, url):
    print("Fetching: ", url)
    try:
        async with session.get(url) as response:
            print("==> ", response.status)
            return await response.text()
    except aiohttp.client_exceptions.ServerDisconnectedError as e:
        print("Exception occurred. Retrying.")
        await fetch(session, url)


def split_name_team(text):
    inner = text.contents
    return inner[0].string, inner[2]


def split_pos(text):
    ret = []
    for d in text:
        if not d.name == 'br':
            ret.append(d)
    return ret


def parse_header(table):
    headers = table.find('td', {'bgcolor': '#CC0033'}).parent.find_all('td')[1:]

    return [header.string for header in headers]


def parse_row(row):
    player = PLAYER_DICT.copy()

    for i, d in enumerate(row.find_all('td')):
        val = d.string

        if val == '-':
            val = 0

        if i == Row.NUMBER:
            player['number'] = val
        elif i == Row.EDITION:
            player['edition'] = val
        elif i == Row.NAME_TEAM:
            name, team  = split_name_team(d)
            player['name'] = name
            player['team'] = team
        elif i == Row.POINTS:
            player['points'] = val
        elif i == Row.YEAR:
            player['year'] = val
        elif i == Row.OBC:
            player['obc'] = val
        elif i == Row.SPD:
            player['spd'] = val
        elif i == Row.POS:
            player['pos'] = split_pos(d)
        elif i == Row.H:
            player['h'] = val
        elif i in (Row.ICON, Row.CHART):
            continue
        elif i == Row.SOG:
            player['sog'] = val
        elif i == Row.BF:
            player['bf'] = val
        elif i == Row.B:
            player['b'] = val
        elif i == Row.W:
            player['w'] = val
        elif i == Row.S:
            player['s'] = val
        elif i == Row.S_PLUS:
            player['s_plus'] = val
        elif i == Row.DB:
            player['db'] = val
        elif i == Row.TR:
            player['tr'] = val
        elif i == Row.HR:
            player['hr'] = val

    return player


def parse_body(rows):
    players = []
    for row in rows:
        if isinstance(row, Tag):
            players.append(parse_row(row))

    return players


def parse_html(raw_html):

    html = BeautifulSoup(raw_html, 'html.parser')
    table = html.find_all('table', {"width": "750"})[2]

    return parse_body(list(table.children)[7:55])

async def fetch_and_parse(sem, session, url, loop):
    async with sem:
        html = await fetch(session, url)
        return parse_html(html)


async def main(loop, config):
    rate = 1.0 / config.rate
    all_players = []
    tasks = []

    sem = asyncio.Semaphore(config.concurrent)

    if config.local:
        with open(config.local, 'rb') as infile:
            html = infile.read()
            data = parse_html(html)
    else:
        async with aiohttp.ClientSession(loop=loop) as session:
            for i in range(NUM_PAGES):
                url = URL.format(numbers=i * PER_PAGE)
                task = asyncio.ensure_future(fetch_and_parse(sem, session, url, loop))
                await asyncio.sleep(rate)
                tasks.append(task)

            all_players = await asyncio.gather(*tasks)
            all_players = list(itertools.chain.from_iterable(all_players))

    with open(config.out, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=PLAYER_DICT.keys())

        writer.writeheader()
        [writer.writerow(player) for player in all_players]


def get_config():
    parser = argparse.ArgumentParser(prog="Showdown Scraper", description="Scrape the showdown card site")

    parser.add_argument("--local", dest="local", help="load local file for testing")

    parser.add_argument("-c", "--concurrenct", dest="concurrent", type=int, default=1, help="Number of concurrent connections")
    parser.add_argument("-r", "--rate", dest="rate", type=int, default=1, help="Requests per second target")

    parser.add_argument("-o", "--outfile", dest="out", default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        help="output file")

    return parser.parse_args()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    config = get_config()

    loop.run_until_complete(main(loop, config))
