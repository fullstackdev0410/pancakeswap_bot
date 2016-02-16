import json


def load_token_config():
    file_to_load = "swap_methods/token_config.json"
    with open(file_to_load, "r") as file_reader: # Read the config file
        config = json.load(file_reader)
    return config


def load_wallet_config():
    file_to_load = "wallets/wallet_config.json"
    with open(file_to_load, "r") as file_reader: # Read the config file
        config = json.load(file_reader)
    return config


def load_abi(address, driver=None):
    filename = f'ABI_{address}.txt'
    with open(f"abi/{filename}") as f:
        abi = f.readlines()
        return abi[0]
