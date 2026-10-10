// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// Stores the hash of each attendance block so the off-chain chain can be verified against Ethereum.
contract AttendanceAnchor {
    address public owner;
    mapping(uint256 => bytes32) public anchors;
    event Anchored(uint256 indexed blockIndex, bytes32 blockHash, uint256 time);

    constructor() { owner = msg.sender; }

    function anchorBlock(uint256 blockIndex, bytes32 blockHash) external {
        require(msg.sender == owner, "Only the faculty/owner can anchor");
        require(anchors[blockIndex] == bytes32(0), "Block already anchored");
        anchors[blockIndex] = blockHash;
        emit Anchored(blockIndex, blockHash, block.timestamp);
    }
}
