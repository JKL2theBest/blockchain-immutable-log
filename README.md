# blockchain-immutable-log
Децентрализованная система неизменяемого аудита критических событий ИТ-инфраструктуры (ImmutableLog).

## ТЕКУЩИЙ СТАТУС
Успешно протестировано сетевое взаимодействие: UI-интерфейс на Streamlit корректно подключается к удаленной ноде Ganache, читает ABI и config.json, и вытягивает реальные записи из смарт-контракта. Автотесты (Pytest) проходят, UI валидирует хэши и ловит подмену файлов. 

# TODO:

# 1. Смарт-контракт (Security Update) - Ответственная: Лиза

```
RemixAI Assistant
Is there any vulnerability in the pasted code?
You
Is there any vulnerability in the pasted code?
AI
This contract does not handle funds or sensitive operations, so it has no direct risk of fund loss or scams. However, it has minor issues:

1. No access control: Anyone can call registerHash, potentially spamming the auditTrail with fake entries.
2. No input validation: _hash could be empty or malformed.
3. Gas costs: Unbounded auditTrail array could make iteration expensive.
No critical vulnerabilities (e.g., reentrancy, overflows) exist. For a production audit log, add access control (e.g., onlyOwner) and input checks.
```

Проверить:

```Solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// NEW: Импортируем стандарт безопасности для управления доступом
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol";

// NEW: Наследуемся от Ownable, чтобы получить модификатор 'onlyOwner'
contract ImmutableLog is Ownable {

    struct LogEntry {
        string fileHash;
        uint256 timestamp;
    }

    LogEntry[] public auditTrail;

    event HashRegistered(string indexed fileHash, uint256 timestamp);

    // NEW: Добавлен модификатор 'onlyOwner'. Теперь эту функцию может вызвать только владелец контракта.
    function registerHash(string memory _hash) public onlyOwner {
        // NEW: Проверка на пустую строку. Если хэш пустой, транзакция будет отменена.
        require(bytes(_hash).length > 0, "Hash cannot be empty");

        auditTrail.push(LogEntry(_hash, block.timestamp));
        emit HashRegistered(_hash, block.timestamp);
    }

    function getLogsCount() public view returns (uint256) {
        return auditTrail.length;
    }
}
```

# 2. Интеграция записи в UI - Ответственный: Мухаммет/Артём

Сейчас кнопка "Записать в блокчейн" в интерфейсе использует `BlockchainServiceMock`. Нужно заменить его на реальный сервис, который будет отправлять транзакции.

**Задачи:**

*   В `src/core/hashing.py` создать новый класс `RealBlockchainService(BlockchainService)`.
*   Перенести логику отправки транзакции из `blockchain/agent.py` внутрь этого класса.
*   Решить вопрос с приватным ключом.

# 3. Рефакторинг и чистота кода - Ответственный: Мухаммет/Лиза

Нужно привести репозиторий в идеальное состояние.

**Задачи:**

*   **Обновить тесты:** Убедиться, что все тесты (`pytest`) продолжают работать после интеграции реального сервиса (все реальные сетевые вызовы в тестах должны быть "замоканы").



# 4. Подготовка финальной документации - Ответственный: Артём

Собрать финальный отчет и презентацию.
