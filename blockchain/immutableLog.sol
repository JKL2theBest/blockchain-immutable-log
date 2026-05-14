// SPDX-License-Identifier: MIT
pragma solidity ^0.8.34;

import "@openzeppelin/contracts/access/Ownable.sol";

contract ImmutableLog is Ownable {
    error EmptyHash();
    error CooldownActive();
    error IndexOutOfBounds();
    error HashAlreadyRegistered();

    struct LogEntry {
        string fileHash;
        uint256 timestamp;
    }

    LogEntry[] private auditTrail;
    
    mapping(string => bool) private _registeredHashes;
    
    mapping(address => uint256) private _lastLogTimestamp;

    uint256 public constant COOLDOWN_PERIOD = 2 seconds;

    event HashRegistered(string indexed fileHash, uint256 indexed timestamp);

    constructor(address initialOwner) Ownable(initialOwner) {}

    function registerHash(string memory fileHash) external onlyOwner {
        if (bytes(fileHash).length == 0) revert EmptyHash();
        
        if (_registeredHashes[fileHash]) revert HashAlreadyRegistered();

        if (block.timestamp < _lastLogTimestamp[msg.sender] + COOLDOWN_PERIOD) {
            revert CooldownActive();
        }

        auditTrail.push(LogEntry({
            fileHash: fileHash,
            timestamp: block.timestamp
        }));

        _registeredHashes[fileHash] = true;
        _lastLogTimestamp[msg.sender] = block.timestamp;

        emit HashRegistered(fileHash, block.timestamp);
    }

    function getLogsCount() external view returns (uint256) {
        return auditTrail.length;
    }

    function getLogEntry(uint256 index) external view returns (LogEntry memory) {
        if (index >= auditTrail.length) revert IndexOutOfBounds();
        return auditTrail[index];
    }
}
