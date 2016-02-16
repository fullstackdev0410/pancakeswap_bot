from utils.utils import load_abi
from swap_methods.web3connector import web3connector

PANCAKE_ROUTER_ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

class Exchange:
    def __init__(self, router_address=PANCAKE_ROUTER_ADDRESS):
        self.web3con = web3connector.connect()
        self.raddress = self.web3con.toChecksumAddress(router_address)
        self.abi = load_abi(self.raddress)
        self.create_contract()

    def create_contract(self):
        self.contract = self.web3con.eth.contract(address=self.raddress, abi=self.abi)