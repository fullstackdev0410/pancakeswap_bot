from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

coinlist = cg.get_coins_list()

for x in coinlist:
    if 'defi' in x['name']:
        print(x)