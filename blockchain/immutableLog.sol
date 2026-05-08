pragma solidity ^0.8.20;
import "@openzeppelin/contracts/access/Ownable.sol";

contract ImmutableLog is Ownable {

    struct LogEntry {
        string fileHash;
        uint256 timestamp;
    }

    LogEntry[] public auditTrail;
    uint256 public lastLogTimestamp;
    uint256 public constant COOLDOWN_PERIOD = 2 seconds;

    event HashRegistered(string indexed fileHash, uint256 timestamp);
    constructor() Ownable(msg.sender) {}
    function registerHash(string memory _hash) public onlyOwner {
        require(bytes(_hash).length > 0, "Hash cannot be empty");
        require(block.timestamp >= lastLogTimestamp + COOLDOWN_PERIOD, "Anti-DDoS: Please wait before sending next log");
        auditTrail.push(LogEntry(_hash, block.timestamp));
        lastLogTimestamp = block.timestamp;
        emit HashRegistered(_hash, block.timestamp);
    }

    function getLogsCount() public view returns (uint256) {
        return auditTrail.length;
    }
}