import hashlib, json, time, os

DIFFICULTY = 3                      # hash must start with "000"
FILE = os.path.join(os.path.dirname(__file__), "chain.json")


class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None, nonce=0):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.strftime("%Y-%m-%d %H:%M:%S")
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = json.dumps({
            "index": self.index, "transactions": self.transactions,
            "previous_hash": self.previous_hash, "timestamp": self.timestamp,
            "nonce": self.nonce}, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def mine(self, difficulty=DIFFICULTY):
        self.hash = self.calculate_hash()
        while not self.hash.startswith("0" * difficulty):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self):
        return {"index": self.index, "transactions": self.transactions,
                "previous_hash": self.previous_hash, "timestamp": self.timestamp,
                "nonce": self.nonce, "hash": self.hash}

    @staticmethod
    def from_dict(d):
        b = Block(d["index"], d["transactions"], d["previous_hash"], d["timestamp"], d["nonce"])
        b.hash = d["hash"]          # keep the STORED hash so tampering stays detectable
        return b


class Blockchain:
    def __init__(self):
        self.chain, self.pending = [], []
        if os.path.exists(FILE):
            self.load()
        else:
            self.reset()

    def reset(self):
        genesis = Block(0, [], "0" * 64)
        genesis.mine()
        self.chain, self.pending = [genesis], []
        self.save()

    def add_transaction(self, tx):
        self.pending.append(tx)
        self.save()

    def mine_pending(self):
        if not self.pending:
            return None
        block = Block(len(self.chain), self.pending, self.chain[-1].hash)
        block.mine()
        self.chain.append(block)
        self.pending = []
        self.save()
        return block

    def validate(self):
        report, ok_so_far = [], True
        for i, b in enumerate(self.chain):
            recalculated = b.calculate_hash()
            hash_ok = recalculated == b.hash and b.hash.startswith("0" * DIFFICULTY)
            link_ok = (b.previous_hash == "0" * 64) if i == 0 else b.previous_hash == self.chain[i - 1].hash
            ok = hash_ok and link_ok and ok_so_far
            ok_so_far = ok_so_far and hash_ok and link_ok
            report.append({"index": b.index, "hash_ok": hash_ok, "link_ok": link_ok,
                           "valid": ok, "recalculated": recalculated})
        return {"valid": all(r["valid"] for r in report), "blocks": report}

    # ---- demo helpers (simulate an attacker) ----
    def tamper(self, block_i, tx_i, status):
        self.chain[block_i].transactions[tx_i]["status"] = status   # no re-hash
        self.save()

    def remine_from(self, block_i):
        for j in range(block_i, len(self.chain)):
            b = self.chain[j]
            b.previous_hash = self.chain[j - 1].hash if j else "0" * 64
            b.nonce = 0
            b.mine()
        self.save()

    def save(self):
        with open(FILE, "w") as f:
            json.dump({"chain": [b.to_dict() for b in self.chain], "pending": self.pending}, f, indent=2)

    def load(self):
        with open(FILE) as f:
            d = json.load(f)
        self.chain = [Block.from_dict(x) for x in d["chain"]]
        self.pending = d["pending"]
