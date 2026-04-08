pragma solidity ^0.8.0;

contract ImmutableLog {

    // Структура, которая хранит хэш файла и точное время записи
    struct LogEntry {
        string fileHash;
        uint256 timestamp;
    }

    // Список всех сохраненных хэшей
    LogEntry[] public auditTrail;

    // Событие для логгирования в блокчейне
    event HashRegistered(string indexed fileHash, uint256 timestamp);

    // Функция: сохранить хэш в блокчейн
    function registerHash(string memory _hash) public {
        // Время берется из сети блокчейна 
        auditTrail.push(LogEntry(_hash, block.timestamp));
        emit HashRegistered(_hash, block.timestamp);
    }

    // Функция: получить количество сохраненных хэшей
    function getLogsCount() public view returns (uint256) {
        return auditTrail.length;
    }
}
