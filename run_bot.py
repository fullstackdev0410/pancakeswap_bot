from pancakeswap import requests_api
#from web3 import Web3
from swap_methods.exchange import Exchange
from swap_methods.swap import Swap
from swap_methods.token import Token
from swap_methods.wallet import Wallet
from swap_methods.web3connector import web3connector
from utils.logutils import get_logger
from utils.utils import load_wallet_config
from swap_methods.volumegenerator import volumeGenerator
# Load configs for token, exchange and wallet

wallet_config = load_wallet_config()
 
WBNB_ADDRESS = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
TOKEN_NAME = 'stakemoon'

web3 = web3connector.connect()

# Argument parser
"""
parser = argparse.ArgumentParser()

parser.add_argument("-t", "--token", default='stakemoon', required=True, help="Token to run bot for")

args = parser.parse_args()
token_name = args.token
# token_name = 'stakemoon'
"""

token_name = 'stakemoon'

# -- request pancakeswap --

ps = requests_api.PancakeSwapAPI()
def get_pancakeswap_info(TokenADR):
    token_info = ps.tokens(TokenADR)
    return token_info

def get_BNB_price(self):
    return self.get_pancakeswap_info()['data']['price_BNB']

# -- BSC --


# Set up logger

logger = get_logger(token_name)

# Initialize wallet info.

w1 = Wallet(wallet_config['WALLET_ADDRESS_1'], wallet_config['PK_1'])
#w2 = Wallet(wallet_config['WALLET_ADDRESS_2'])

stmToken = Token(TOKEN_NAME)

def print_info(Wallet, Token):
    print(f"Wallet {Wallet.ADR[-4:]} contains {web3.eth.get_balance(Wallet.ADR)} BNB and {Token.check_balance(Wallet.ADR)} {Token.token_name}")

print_info(w1, stmToken)
#print_info(w2, stmToken)

# Create a contract for both PancakeRoute and Token to Sell

pancakeObj = Exchange()

tradeObj = Swap(wallet=w1, token=stmToken, exchange=pancakeObj)

# res = tradeObj.buy_token(token_amount_in_spend_token=toBuyBNBAmount)

w1.get_balance(stmToken)
w1.balances

# web3.eth.getTransaction('0x8009227d6fd72e962fdf19974d747548080d864b8af1f6689196de724fcba8e0')
# web3.eth.getTransactionReceipt('0x8009227d6fd72e962fdf19974d747548080d864b8af1f6689196de724fcba8e0')
# 0x8009227d6fd72e962fdf19974d747548080d864b8af1f6689196de724fcba8e0
# web3.eth.getTransactionReceipt('0x42dbafddaa1b578de8026aed4aa749a35736ce075bf296602c2266b3a01cc55d')
# web3.eth.getTransactionReceipt('0x15d1b78aa3616a6fca4a6100cc1287684c1769b992ad9c2097fdd8519b13eb03')

vg = volumeGenerator(wallet=w1, token=stmToken, exchange=pancakeObj)
vg.get_wallet_state()
# vg.buy(0.0025)

# Does not work.

pancakeObj = Exchange()
stmToken = Token(TOKEN_NAME)
w1 = Wallet(wallet_config['WALLET_ADDRESS_1'], wallet_config['PK_1'])
w1.balances
vg = volumeGenerator(wallet=w1, token=stmToken, exchange=pancakeObj)
vg.run()
# vg.sell(10000000000000, convert=False)




