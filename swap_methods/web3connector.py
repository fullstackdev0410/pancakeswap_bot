from web3 import Web3

class web3connector:
    # TO DO - Make singleton?
    def __init__(self):
        self.connection = None
    @staticmethod
    def connect():
        bsc_link = 'https://bsc-dataseed.binance.org/'
        connection = Web3(Web3.HTTPProvider(bsc_link))
        return connection