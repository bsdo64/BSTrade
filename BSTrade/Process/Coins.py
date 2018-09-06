import json
import os
import shutil
import requests as r
import asyncio
import aiohttp

PATH = os.getcwd() + '/BSTrade/static'

coin_info_url = 'https://s2.coinmarketcap.com/generated/search' \
                '/quick_search.json'
img_info_url = 'https://s2.coinmarketcap.com/static/img/coins/128x128'
filename = PATH + '/coins.json'
save_dir = PATH + '/img/coins'


def refresh_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path)
        os.mkdir(path)


async def fetch(client, item):
    url = img_info_url + '/{}.png'.format(item['img_id'])

    async with client.get(url) as resp:
        assert resp.status == 200
        img_b = await resp.read()
        with open(save_dir + '/{}.png'.format(item['slug']), 'wb') as f:
            f.write(img_b)


async def main(coins):
    async with aiohttp.ClientSession() as client:
        await asyncio.gather(*[
            asyncio.ensure_future(fetch(client, item))
            for item in coins
        ])


def request():
    print('request coin info')

    try:
        database = open(filename).read()
        db_json = json.loads(database)
    except FileNotFoundError:
        db_json = []

    res = r.get(coin_info_url).json()
    coin_info = [{
        'name': coin['name'],
        'slug': coin['slug'],
        'img_id': coin['id'],
        'symbol': coin['symbol'],
    } for coin in res]

    coin_ids = {coin['img_id'] for coin in coin_info}
    database_ids = {coin['img_id'] for coin in db_json}
    coin_ids -= database_ids
    need_request = [coin for coin in coin_info if coin['img_id'] in coin_ids]

    if need_request:
        refresh_dir(save_dir)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(coin_info))

        with open(filename, 'wb') as f:
            f.write(bytes(json.dumps(coin_info), encoding='utf-8'))

    print('request coin success..')
