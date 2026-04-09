import json
from web3 import Web3


def send_log_to_blockchain(log_message):
    print(f"Отправка лога: {log_message}")
    tx_hash = contract.functions.registerHash(log_message).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Успешно! Блок: {receipt.blockNumber}")
    return tx_hash.hex()


with open("config.json", "r") as f:
    config = json.load(f)

with open("abi.json", "r") as f:
    contract_abi = json.load(f)

w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
w3.eth.default_account = w3.eth.accounts[0]

contract = w3.eth.contract(address=config["contract_address"], abi=contract_abi)

send_log_to_blockchain("Test log =)")