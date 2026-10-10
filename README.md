# AttendChain: Blockchain-Based Student Attendance Management

BIC702 Blockchain Technology, Group 2 project.

AttendChain records student attendance as transactions in a SHA-256 blockchain written in Python. Records are grouped into mined blocks and linked by hashes, so any edit is detectable. Each block's hash is also anchored on the Ethereum Sepolia test network through a Solidity smart contract, which catches tampering even when someone re-mines the local chain.

## Table of contents

1. [Problem](#problem)
2. [How it works](#how-it-works)
3. [Architecture](#architecture)
4. [Project structure](#project-structure)
5. [Component details](#component-details)
6. [API reference](#api-reference)
7. [Setup and run](#setup-and-run)
8. [Deploying the smart contract](#deploying-the-smart-contract)
9. [Demo walkthrough](#demo-walkthrough)
10. [Limitations](#limitations)
11. [Tech stack](#tech-stack)

## Problem

Attendance is usually kept on paper, in spreadsheets or in a portal controlled by one administrator. Records can be edited quietly, there is no audit trail, and nobody outside the system can prove that a record is unchanged. A blockchain makes edits visible because every block depends on the one before it.

## How it works

1. Faculty enter attendance (student ID, name, subject, date, Present or Absent). Each entry is a **transaction** that waits in a pending list.
2. **Mining** groups the pending transactions into a **block**. The program searches for a nonce that makes the block's SHA-256 hash start with `000` (proof of work).
3. Each block stores the **previous block's hash**, which chains the blocks together.
4. **Validation** recalculates every block's hash and checks the links. If one block changes, it and all later blocks fail validation.
5. The block hash can be **anchored** on Ethereum Sepolia. The contract stores it permanently and refuses to overwrite it.
6. **Verification** compares each local block hash with the hash stored on Sepolia. A mismatch proves the local chain was altered, even if the attacker re-mined everything.

## Architecture

```
 Browser (index.html + ethers.js)
    |  fetch /api/...                |  MetaMask (Sepolia)
    v                                v
 Flask server (app.py)         AttendanceAnchor.sol
    |                          (block index -> block hash)
    v
 blockchain.py  --->  chain.json (local ledger)
```

## Project structure

```
attendance-blockchain/
├── app.py                         Flask server and API routes
├── blockchain.py                  Block and Blockchain classes
├── requirements.txt               Python dependencies
├── templates/
│   └── index.html                 Web interface and MetaMask code
├── contracts/
│   └── AttendanceAnchor.sol       Solidity smart contract
├── screenshots/                   Project screenshots
└── chain.json                     Local ledger (auto-created, git-ignored)
```

## Component details

### blockchain.py

| Part | Purpose |
|---|---|
| `Block` | Holds index, transactions, previous hash, timestamp, nonce and hash |
| `calculate_hash()` | SHA-256 over the block's fields |
| `mine()` | Increases the nonce until the hash starts with `000` |
| `Blockchain` | Manages the chain, the pending list and saving to `chain.json` |
| `mine_pending()` | Turns pending transactions into a new block |
| `validate()` | Per block: recalculated hash equals stored hash, and the previous-hash link is correct |
| `tamper()` | Demo helper: edits a record without re-hashing |
| `remine_from()` | Demo helper: simulates an attacker recalculating hashes |

### app.py

A Flask server that serves the web page and exposes the blockchain through JSON routes. It validates input (student ID and name required, status must be Present or Absent).

### templates/index.html

The user interface: attendance form, mining, student lookup, chain viewer with stored versus recalculated hashes, and the Ethereum panel (connect MetaMask, anchor a block, verify against Sepolia). The page uses ethers.js from a CDN.

### contracts/AttendanceAnchor.sol

| Item | Behaviour |
|---|---|
| `owner` | The wallet that deployed the contract (acts as faculty) |
| `anchorBlock(index, hash)` | Stores a block hash, owner only, one time per block index |
| `anchors(index)` | Public read of a stored hash |
| `Anchored` event | Emitted on every anchor, visible on Etherscan |

## API reference

| Method and route | Description |
|---|---|
| `GET /api/state` | Chain, pending entries and validation report |
| `POST /api/attendance` | Add a transaction to the pending list |
| `POST /api/mine` | Mine pending transactions into a block |
| `GET /api/student/<id>` | Attendance history of one student |
| `POST /api/tamper` | Demo only: change a record without re-hashing |
| `POST /api/remine` | Demo only: recalculate hashes from a block onward |
| `POST /api/reset` | Clear the ledger back to the genesis block |

## Setup and run

Requirements: Python 3.11 or newer, a Chromium-based browser with the MetaMask extension.

```
git clone https://github.com/YOUR-USERNAME/attendance-blockchain.git
cd attendance-blockchain
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. On Mac or Linux, use `python3` and `source venv/bin/activate`.

## Deploying the smart contract

1. Install MetaMask, enable test networks and select **Sepolia**.
2. Get free test ETH from a Sepolia faucet.
3. Open [remix.ethereum.org](https://remix.ethereum.org) and create `AttendanceAnchor.sol` with the code from `contracts/`.
4. Compile with Solidity 0.8.20 or newer.
5. In Deploy and Run, choose **Injected Provider - MetaMask** and click Deploy.
6. Paste the deployed contract address into the app's Ethereum panel.

Deployed contract address: `0xYOUR_CONTRACT_ADDRESS`

## Demo walkthrough

1. Add a few attendance entries and click **Mine block**.
2. Click **Validate chain**. All blocks are green and the links match.
3. Connect MetaMask and click **Anchor latest block** for each block.
4. Click **Flip status** on a transaction. The block's recalculated hash differs from its stored hash, and it and all later blocks turn red.
5. Click **Attacker re-mines from here**. The local chain is valid again, which shows a local-only chain can be rewritten.
6. Click **Verify chain against Sepolia**. The edited block shows **MISMATCH**, so the tampering is caught.

## Limitations

- The local ledger runs on one node. Decentralization is demonstrated through Sepolia.
- Proof of work is not needed in a private college network. Proof of authority would be more practical.
- Student data is personal, so only hashes are put on the public chain.
- Anchoring costs gas on a real network.
- The blockchain protects records after they are written, not the honesty of whoever enters them.

## Tech stack

Python, Flask, HTML and JavaScript, ethers.js, Solidity, Remix IDE, MetaMask, Ethereum Sepolia testnet.
