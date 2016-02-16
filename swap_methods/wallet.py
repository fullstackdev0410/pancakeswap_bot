from swap_methods.token import Token
import datetime
from utils.logutils import get_logger

logger = get_logger('balances')

class Wallet:
    def __init__(self, address, private_key=None):
        self.ADR = address
        self.PK = private_key
        self.balances = {}

    def get_balance(self, token:Token):
        balance = token.check_balance(self.ADR)
        self.balances[token.token_name] = {'balance': balance,
                                          'updated': datetime.datetime.utcnow()}
        logger.info(f'Balance in {self.ADR} of {token.token_name} at {str(datetime.datetime.utcnow())} is {balance}')
        return balance

