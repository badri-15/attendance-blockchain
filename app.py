from flask import Flask, jsonify, request, render_template
from blockchain import Blockchain
import time

app = Flask(__name__)
bc = Blockchain()


def state():
    return {"chain": [b.to_dict() for b in bc.chain], "pending": bc.pending,
            "validation": bc.validate()}


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/api/state")
def get_state():
    return jsonify(state())


@app.post("/api/attendance")
def add_attendance():
    d = request.get_json(force=True)
    sid, name = str(d.get("student_id", "")).strip(), str(d.get("name", "")).strip()
    status = d.get("status")
    if not sid or not name or status not in ("Present", "Absent"):
        return jsonify({"error": "student_id, name and status (Present/Absent) are required"}), 400
    bc.add_transaction({"student_id": sid, "name": name,
                        "subject": str(d.get("subject", "")).strip() or "-",
                        "date": d.get("date") or time.strftime("%Y-%m-%d"), "status": status})
    return jsonify(state())


@app.post("/api/mine")
def mine():
    if bc.mine_pending() is None:
        return jsonify({"error": "No pending attendance entries to mine"}), 400
    return jsonify(state())


@app.get("/api/student/<sid>")
def student(sid):
    rows = [dict(t, block=b.index) for b in bc.chain for t in b.transactions if t["student_id"] == sid]
    return jsonify(rows)


@app.post("/api/tamper")
def tamper():
    d = request.get_json(force=True)
    bc.tamper(int(d["block"]), int(d["tx"]), d["status"])
    return jsonify(state())


@app.post("/api/remine")
def remine():
    bc.remine_from(int(request.get_json(force=True)["block"]))
    return jsonify(state())


@app.post("/api/reset")
def reset():
    bc.reset()
    return jsonify(state())


if __name__ == "__main__":
    app.run(debug=True)
