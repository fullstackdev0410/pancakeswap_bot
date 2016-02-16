import time

from swap_methods.web3connector import web3connector
from swap_methods.exchange import Exchange
from swap_methods.token import Token
from swap_methods.wallet import Wallet

WBNB_ADDRESS = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

class Swap:
    def __init__(self, wallet: Wallet, token: Token, exchange: Exchange):
        # Class to trade token vs BNB on a specific wallet
        self.wallet = wallet
        self.token = token
        self.exchange = exchange
        self.web3con = web3connector.connect()
        self.panRouterContractAddress = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
        self.gasPrice = 100
        self.gasPrice_sell = 10

        #
        self.target_token = self.token.TokenADR
        self.bnb_token = WBNB_ADDRESS


    def setup_contract(self, token_to_spend, token_to_buy, token_amount_in_spend_token, convert = True):
        """
        pancakeSwap_txn = self.exchange.contract.functions.swapExactETHForTokens(
            0,
            [token_to_spend, token_to_buy],
            self.wallet.ADR,
            (int(time.time() + 10000))).buildTransaction({
            'from': self.wallet.ADR,
            'value': token_amount_in_spend_token,  # Amount of BNB if BNB --> XXXX
            'gas': 160000,
            'gasPrice': web3con.toWei('5', 'gwei'),
            'nonce': web3con.eth.get_transaction_count(self.wallet.ADR)
        })
        """
        transactionRevertTime = 100000
        gasAmount = 300000
        nonce = self.web3con.eth.get_transaction_count(self.wallet.ADR)
        value = token_amount_in_spend_token

        pancakeswap2_txn = self.exchange.contract.functions.swapExactETHForTokens(
        0, # Set to 0 or specify min number of swap_methods - setting to 0 just buys X amount of token at its current price for whatever BNB specified
        [token_to_spend, token_to_buy],
        self.wallet.ADR,
        (int(time.time()) + transactionRevertTime)
        ).buildTransaction({
        'from': self.wallet.ADR,
        'value': value, #This is the Token(BNB) amount you want to Swap from
        'gas': gasAmount,
        'gasPrice': self.web3con.toWei(self.gasPrice,'gwei'),
        'nonce': nonce,
        })
        return pancakeswap2_txn

    def setup_sell_contract(self, token_to_spend, token_to_buy, token_amount_in_spend_token):
        """
        when you try to sell and the tokens received < amountOutMin it fails

        :param token_to_spend: Should be the pump token
        :param token_to_buy: Should be BNB
        :param token_amount_in_spend_token:
        :return:
        """
        sellTokenContract = self.web3con.eth.contract(token_to_spend, abi=self.token.token_abi)
        balance = sellTokenContract.functions.balanceOf(self.wallet.ADR).call()
        symbol = sellTokenContract.functions.symbol().call()
        gasAmount = 200000
        nonce = self.web3con.eth.get_transaction_count(self.wallet.ADR)
        approve = sellTokenContract.functions.approve(self.panRouterContractAddress, balance).buildTransaction({
            #'from': self.wallet.ADR,
            #'gasPrice': self.web3con.toWei('5', 'gwei'),
            #'nonce': self.web3con.eth.get_transaction_count(self.wallet.ADR),
            'chainId': self.web3con.eth.chainId,
            'nonce': nonce,
            'gas': gasAmount,
            'gasPrice': self.web3con.toWei(10, 'gwei'),
        })

        signed_txn = self.web3con.eth.account.sign_transaction(approve, private_key=self.wallet.PK)
        tx_token = self.web3con.eth.send_raw_transaction(signed_txn.rawTransaction)
        print("Approved: " + self.web3con.toHex(tx_token))

        transactionRevertTime = 100000

        sellTxn = self.exchange.contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
            token_amount_in_spend_token,
            0,
            [token_to_spend, token_to_buy],
            self.wallet.ADR,
            (int(time.time()) + transactionRevertTime)
            ).buildTransaction({
                'from': self.wallet.ADR,
                'gasPrice': self.web3con.toWei(self.gasPrice_sell, 'gwei'),
                'nonce': nonce+1,
        })
        # sellTxn = self.exchange.contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
        #     token_amount_in_spend_token,
        #     0,
        #     [token_to_spend, token_to_buy],
        #     self.wallet.ADR,
        #     (int(time.time()) + transactionRevertTime)
        #     ).buildTransaction({
        #     'chainId': self.web3con.eth.chainId,
        #     'nonce': nonce,
        #     'gas': gasAmount,
        #     'gasPrice': self.web3con.toWei(self.gasPrice,'gwei')
        # })

        return sellTxn

    def send_transaction(self, ps_txn,  amount):
        signed_txn = self.web3con.eth.account.sign_transaction(ps_txn, private_key=self.wallet.PK)
        tx_token = self.web3con.eth.send_raw_transaction(signed_txn.rawTransaction)
        result = [self.web3con.toHex(tx_token), f"Bought {self.web3con.fromWei(amount, 'ether')} BNB of {self.token.token_name}"]
        return result

    def get_bnb_balance(self):
        return self.web3con.eth.get_balance(self.wallet.ADR)

    def buy_token(self, token_amount_in_spend_token, convert=True):

        if convert:
            value = self.web3con.toWei(float(token_amount_in_spend_token), 'ether')
        else:
            value = token_amount_in_spend_token

        txn = self.setup_contract(token_to_spend=self.bnb_token,
                                  token_to_buy=self.target_token,
                                  token_amount_in_spend_token=value)
        res = self.send_transaction(txn, value)
        return res

    def sell_token(self, token_amount_in_spend_token, convert=True):

        if convert:
            value = self.web3con.toWei(float(token_amount_in_spend_token), 'ether')
        else:
            value = token_amount_in_spend_token

        txn = self.setup_sell_contract(token_to_spend=self.target_token,
                                       token_to_buy=self.bnb_token,
                                       token_amount_in_spend_token=value)
        res = self.send_transaction(txn, value)
        return res

