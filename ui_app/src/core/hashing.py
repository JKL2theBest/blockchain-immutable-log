import hashlib
import time
from abc import ABC, abstractmethod
from typing import final, cast
import os
from eth_account import Account
from dotenv import load_dotenv
from eth_typing import ChecksumAddress
from web3 import Web3
from web3.middleware.proof_of_authority import ExtraDataToPOAMiddleware

load_dotenv()


class BlockchainService(ABC):
    """
    Абстрактный базовый класс для сервиса взаимодействия с блокчейном.
    Определяет контракт, которому должны следовать все реализации (реальные или моки).
    """

    @abstractmethod
    def register_hash(self, file_hash: str) -> str:
        """Регистрирует хэш файла в смарт-контракте."""
        pass

    @abstractmethod
    def get_all_logs(self) -> list[dict]:
        """Получает все записи из смарт-контракта."""
        pass


class RealBlockchainService(BlockchainService):
    """
    Реальный сервис взаимодействия со смарт-контрактом через Web3.py.
    """

    def __init__(self, abi: list):
        rpc_url = os.getenv("WEB3_RPC_URL")
        contract_address = os.getenv("CONTRACT_ADDRESS")

        if not rpc_url or not contract_address:
            raise ValueError("WEB3_RPC_URL или CONTRACT_ADDRESS не найдены в .env")

        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        if not self.w3.is_connected():
            raise ConnectionError(f"Не удалось подключиться к сети: {rpc_url}")

        checksum_address = cast(
            ChecksumAddress, Web3.to_checksum_address(contract_address)
        )
        self.contract = self.w3.eth.contract(address=checksum_address, abi=abi)

        self.chain_id = int(os.getenv("WEB3_CHAIN_ID", 1337))

    def register_hash(self, log_hash: str) -> str:
        pk = os.getenv("OWNER_PRIVATE_KEY")
        if not pk:
            raise Exception("OWNER_PRIVATE_KEY не найден в .env")

        account = Account.from_key(pk)

        # Проверка владельца
        try:
            contract_owner = self.contract.functions.owner().call()
            if account.address.lower() != contract_owner.lower():
                raise Exception("execution reverted: OwnableUnauthorizedAccount")
        except Exception as e:
            if "OwnableUnauthorizedAccount" in str(e):
                raise e

        nonce = self.w3.eth.get_transaction_count(account.address)

        # Динамический chainId
        dict_transaction = self.contract.functions.registerHash(
            log_hash
        ).build_transaction(
            {
                "chainId": self.chain_id,
                "gas": 500000,
                "gasPrice": self.w3.to_wei("1", "gwei"),
                "nonce": nonce,
                "from": account.address,
            }
        )

        signed_tx = self.w3.eth.account.sign_transaction(
            dict_transaction, private_key=pk
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash.hex()

    def get_all_logs(self) -> list[dict]:
        """Считывает все сохраненные логи напрямую из смарт-контракта."""
        try:
            total_logs = self.contract.functions.getLogsCount().call()
            logs = []
            for i in range(total_logs):
                log_data = self.contract.functions.auditTrail(i).call()
                logs.append(
                    {
                        "Хэш файла (SHA-256)": log_data[0],
                        "Timestamp (Блокчейн)": log_data[1],
                    }
                )
            return logs
        except Exception as e:
            raise RuntimeError(f"Ошибка при чтении из блокчейна: {e}") from e


@final
class BlockchainServiceMock(BlockchainService):
    """Класс-заглушка (Mock) для имитации работы с блокчейном."""

    _MOCK_STORAGE: list[dict[str, str | int]] = []

    def register_hash(self, file_hash: str) -> str:
        """Имитирует отправку хэша в смарт-контракт."""
        print(f"[*] Имитация отправки хэша '{file_hash[:10]}...' в блокчейн...")
        time.sleep(1)
        self._MOCK_STORAGE.append(
            {
                "Хэш файла (SHA-256)": file_hash,
                "Timestamp (Блокчейн)": int(time.time()),
            }
        )
        mock_tx_hash = f"0x{hashlib.sha256(file_hash.encode()).hexdigest()[:40]}"
        print(f"[+] Хэш успешно зарегистрирован в транзакции: {mock_tx_hash}")
        return mock_tx_hash

    def get_all_logs(self) -> list[dict]:
        """Возвращает данные из мок-хранилища."""
        print("[*] Чтение данных из Mock-хранилища...")
        return self._MOCK_STORAGE


def calculate_sha256(file_bytes: bytes) -> str:
    """Вычисляет SHA-256 хэш для содержимого файла."""
    if not file_bytes:
        raise ValueError("Нельзя хэшировать пустой файл.")
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_bytes)
    return sha256_hash.hexdigest()
