import datetime
import random
import time
from utils.logutils import get_logger
import csv
from web3.exceptions import TransactionNotFound

from swap_methods.exchange import Exchange
from swap_methods.swap import Swap
from swap_methods.token import Token
from swap_methods.wallet import Wallet
import os
import pandas as pd


logger = get_logger('vg')


def get_new_time_to_perform_action(lower_mins=30):
    delay_minutes = (lower_mins + random.random() * 30)  # 30-60 minutes
    return time.time() + delay_minutes * 60


class volumeGenerator:
    def __init__(self, wallet: Wallet, token: Token, exchange: Exchange, target_volume_BNB = 1):

        self.token = token
        self.wallet = wallet
        self.exchange = exchange

        self.token_name = token.token_name

        self.min_bnb = 0.05
        self.max_bnb = 0.5
        self.bnb_perc = 0.01
        self.token_perc = 0.01

        self.min_token = 10000000000
        self.max_token = 51996844433139 # make this dynamic

        self.swapper = Swap(wallet=wallet, token=token, exchange=exchange)

        self.wallet_state = {}
        self.update_wallet_state()
        self.dirname = 'trade_data'
        print(f"Initializing volumeGenerator for token {token.token_name} and wallet ending in {wallet.ADR[-6:]} with {self.wallet_state['current_state']['bnb']} BNB and {self.wallet_state['current_state']['token']} {token.token_name} ")
        #print(f"Wallet {token.token_name} and wallet ending in {wallet.ADR[-6:]}")
        self.row_header = ['datetime', 'type', 'amount', 'tx', 'wallet', 'gas']
        self.refresh_trade_data()


    def update_wallet_state(self):
        if 'current_state' in self.wallet_state:
            self.wallet_state['previous_state'] = self.wallet_state.pop('current_state')
        self.wallet_state['current_state'] = self.get_wallet_state()

    def get_wallet_state(self):
        wallet_state = {
            'time_update': datetime.datetime.utcnow(),
            'bnb': self.swapper.get_bnb_balance(),
            'token': self.wallet.get_balance(self.token)
        }

        return wallet_state

    def get_amount_spent(self):
        if 'previous_state' in self.wallet_state and 'current_state' in self.wallet_state:
            change_in_bnb = self.wallet_state['current_state']['bnb'] - self.wallet_state['previous_state']['bnb']
            change_in_token = self.wallet_state['current_state']['token'] - self.wallet_state['previous_state']['token']
            return change_in_bnb, change_in_token
        else:
            return None, None

    def get_transation_info(self, tx, sleep_wait_time_for_receipt=10):
        try:
            tx_attribute = self.swapper.web3con.eth.getTransactionReceipt(tx)
        except TransactionNotFound:
            print("Waiting on transaction receipt")
            time.sleep(sleep_wait_time_for_receipt)
            tx_attribute = self.swapper.web3con.eth.getTransactionReceipt(tx)
        return tx_attribute

    def create_transaction_info(self, tx):

        tx_ = self.get_transation_info(tx)
        self.update_wallet_state()
        change_in_bnb, change_in_token = self.get_amount_spent()

        gas_used = self.exchange.web3con.toWei(tx_['gasUsed']*self.swapper.gasPrice, 'gwei')
        if change_in_bnb is None:
            perc_gas = None
        elif change_in_bnb != 0:
            perc_gas = abs(gas_used / float(change_in_bnb) * 100)
        else:
            perc_gas = None

        bnb_wallet = self.wallet_state['previous_state']['bnb']
        perc_spent_bnb = round(change_in_bnb/float(bnb_wallet)*100, 2)

        logger.info(f"Transaction receipt received: BNB changed by {change_in_bnb} BNB to {self.wallet_state['current_state']['bnb']} from {self.wallet_state['previous_state']['bnb']}  BNB ({perc_spent_bnb}% of wallet total) for {change_in_token} {self.token_name}. Spent {gas_used} ({perc_gas}%) gas")

        return gas_used

    def buy_perc_wallet(self, perc:float):
        self.update_wallet_state()
        v = perc * self.wallet_state['current_state']['bnb']
        
        if v < self.min_bnb:
            self.buy_token_flag = False
            return

        if v > self.max_bnb:
            v = self.max_bnb

        trade_info = self.buy(amount=v, convert=False)
        self.refresh_trade_data(tradeinfo=trade_info)

    def sell_perc_wallet(self, perc:float):
        self.update_wallet_state()
        v = perc * self.wallet_state['current_state']['token']
        
        if v < self.min_token:
            self.buy_token_flag = True
            return

        if v > self.max_token:
            v = self.max_token

        trade_info =self.sell(amount=v, convert=False)
        self.refresh_trade_data(tradeinfo=trade_info)

    def buy(self, amount, convert=True):
        res = self.swapper.buy_token(amount, convert=convert)
        logger.info(f"Transaction sent for buy token amount {amount}: {res[0]}")
        time.sleep(2)
        gas_used = self.create_transaction_info(res[0])

        trade_info = {
                    'datetime': datetime.datetime.utcnow(),
                    'type': 'buy',
                    'amount': amount,
                    'tx': res[0],
                    'wallet': self.wallet.ADR,
                    'amount_dollar': amount,
                    'gas': gas_used,
                    'walletstate_bnb': self.wallet_state['current_state']['bnb'],
                    'walletstate_token': self.wallet_state['current_state']['token'],
        }

        return trade_info

    def sell(self, amount, convert=True):
        res = self.swapper.sell_token(amount, convert=convert)
        logger.info(f"Transaction sent for sell token amount {amount}: {res[0]}")
        time.sleep(2)
        gas_used = self.create_transaction_info(res[0])

        trade_info = {
            'datetime': datetime.datetime.utcnow(),
            'type': 'buy',
            'amount': amount,
            'tx': res[0],
            'wallet': self.wallet.ADR,
            'amount_dollar': amount,
            'gas': gas_used,
            'walletstate_bnb': self.wallet_state['current_state']['bnb'],
            'walletstate_token': self.wallet_state['current_state']['token'],
        }

        return trade_info

    def run(self):

        next_time_to_run = get_new_time_to_perform_action()
        while True:
            if time.time() > next_time_to_run:
                next_time_to_run = get_new_time_to_perform_action()
                if self.buy_token_flag:
                    self.buy_perc_wallet(self.bnb_perc)
                else:
                    self.sell_perc_wallet(self.token_perc)


            # if time.time() >= next_time_to_run:
            #     next_time_to_run = get_new_time_to_perform_action()
            #     # BUY / SELL according to condition

            # else:
            #     time.sleep(30)

    def refresh_trade_data(self, tradeinfo=None):

        self.check_trade_log()

        if tradeinfo is not None:
            self.save_trade(tradeinfo)

        self.df_trades = self.get_todays_trade_data()

        return

    def save_trade(self, trade_info):

        data_to_insert = []
        for header_name in self.row_header:
            if header_name in trade_info:
                data_to_insert.append(trade_info[header_name])
            else:
                data_to_insert.append('')

        savefile_name = self.return_trade_log_name()

        with open(savefile_name, 'a') as fd:
            writer = csv.writer(fd)
            writer.writerow(trade_info)

    def get_todays_trade_data(self):

        trade_log_file_name = self.return_trade_log_name()
        df = pd.read_csv(trade_log_file_name)

        print(self.df_trades['amount_dollar'].sum())

        return df

    def return_trade_log_name(self, date=datetime.date.today()):
        if isinstance(date, str):
            datetag = date
        else:
            datetag = date.strftime('%Y%m%d')

        filename = 'trades_' + datetag + '.csv'
        savefile_name = os.path.join(self.dirname, filename)

        return savefile_name

    def load_tradelog(self, date):
        filname = self.return_trade_log_name(date)
        df = pd.read_csv(filname)
        return df

    def check_trade_log(self):

        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

        filename = self.return_trade_log_name()

        if not os.path.exists(filename):
            with open(filename, 'a') as output_file:
                writer = csv.writer(output_file)
                writer.writerow(self.row_header)

        return filename

    def get_traded_volume_date(self, date=datetime.date.today()):
        df = self.load_tradelog(date)
        return df['amount_dollar'].sum()