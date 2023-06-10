pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

contract AuditAttestation is Ownable {
    mapping(address => bool) public auditCompleted;
    mapping(address => string) public auditURL;
    mapping(address => bytes32) public auditChecksum;

    event AuditRequested(address indexed contractAddress);
    event AuditResultSet(address indexed contractAddress, string url, bytes32 checksum);

    function requestAudit(address contractAddress) external payable {
        require(msg.value >= 0.01 ether, "Insufficient payment for audit request");

        // Refund if this audit has already been paid for
        // TODO what happens if we want to rerequest?
        require(auditCompleted[contractAddress] == false, "Audit already compelted");

        emit AuditRequested(contractAddress);
    }

    function checkAudit(address contractAddress) external view returns (string memory url, bytes32 checksum) {
        require(auditCompleted[contractAddress], "No audit result available for this address");

        return (auditURL[contractAddress], auditChecksum[contractAddress]);
    }

    function setAuditResult(address contractAddress, string calldata url, bytes32 checksum) external onlyOwner {
        auditURL[contractAddress] = url;
        auditChecksum[contractAddress] = checksum;
        auditCompleted[contractAddress] = true;
        emit AuditResultSet(contractAddress, url, checksum);
    }
}
