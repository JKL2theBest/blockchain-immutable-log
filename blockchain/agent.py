import json
import hashlib
import os
import time
from web3 import Web3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
ABI_PATH = os.path.join(BASE_DIR, "abi.json")
SHADOW_DB_PATH = os.path.join(BASE_DIR, "..", "shadow_db.json")


def hash_log_line(line: str) -> str:
    return hashlib.sha256(line.strip().encode('utf-8')).hexdigest()


def main():
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    with open(ABI_PATH, "r") as f:
        abi = json.load(f)

    w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
    PRIVATE_KEY = "private_key"
    account = w3.eth.account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(address=config["contract_address"], abi=abi)
    if os.path.exists(SHADOW_DB_PATH):
        with open(SHADOW_DB_PATH, "r") as f:
            shadow_db = json.load(f)
    else:
        shadow_db = {}

    log_filepath = os.path.join(BASE_DIR, "..", "ui_app", "tests", "fixtures", "original_log.txt")
    print(f"Агент запущен. Мониторинг файла: {log_filepath}")

    with open(log_filepath, 'r') as file:
        for line in file:
            if "SECURITY" in line or "admin" in line or "root" in line:
                log_hash = hash_log_line(line)

                if log_hash not in shadow_db:
                    print(f"\n[!] Найдено критическое событие: {line.strip()}")
                    shadow_db[log_hash] = line.strip()
                    with open(SHADOW_DB_PATH, "w") as f:
                        json.dump(shadow_db, f, indent=4, ensure_ascii=False)
                    nonce = w3.eth.get_transaction_count(account.address)
                    tx = contract.functions.registerHash(log_hash).build_transaction({
                        'chainId': 1337,
                        'gas': 2000000,
                        'gasPrice': w3.to_wei('20', 'gwei'),
                        'nonce': nonce,
                    })
                    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                    w3.eth.wait_for_transaction_receipt(tx_hash)
                    print(f"Хэш {log_hash[:8]}... записан.")
                    time.sleep(3)


if __name__ == "__main__":
    main()