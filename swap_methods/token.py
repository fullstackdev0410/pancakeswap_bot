from utils.utils import load_abi, load_token_config
from swap_methods.web3connector import web3connector

tokens_config = load_token_config()

class Token:
    def __init__(self, tokenname):
        self.web3con = web3connector.connect()
        self.token_name = tokenname
        self.web3token = None
        self.token_address = tokens_config[tokenname]
        self.token_abi = load_abi(self.token_address)
        self.TokenADR = self.web3con.toChecksumAddress(self.token_address)

        self.ps = None

    def init_token_contract(self):
        self.web3token = self.web3con.eth.contract(address=self.TokenADR,
                                              abi=self.token_abi)

    def check_balance(self, wallet_address):
        if self.web3token is None:
            self.init_token_contract()
        token_balance = self.web3token.functions.balanceOf(wallet_address).call()  # returns int with balance, without decimals

        return token_balance
