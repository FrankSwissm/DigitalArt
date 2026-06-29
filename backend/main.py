import json
import os
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='../frontend/public', static_url_path='')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIX_PATH = os.path.join(BASE_DIR, "config", "kemet_matrix.json")
TIERS_PATH = os.path.join(BASE_DIR, "config", "user_tiers.json")

# ─── CORE INTEGRATION ENDPOINTS ──────────────────────────────────────
SEMHAL_ECOSYSTEM_URL = "https://semhal-crypto.onrender.com"

# Re-routed to your explicit Milar Digital Art Asset target account
TARGET_WALLET = "0x0A5AbC999e6880059B321496336BC173A1667AF0"

# ─── RE-CALIBRATED ECONOMIC PARAMETERS ───────────────────────────────
TOTAL_SHARDS = 1000000000              # Expanded to 1,000,000,000 shards
TOTAL_PRICE_USD = 1000000000000         # Total Cap: 1,000,000,000,000 USD
PRICE_PER_SHARD = 1000.00               # 1 Shard = 1,000 USD / SUSD

# Shard Deduction & Allocation Architecture for 101 Deities:
SOLD_SHARDS = 86866200
REMAINING_SHARDS = TOTAL_SHARDS - SOLD_SHARDS  # 913,133,800 Shards remaining
DEITY_COUNT = 101
SHARDS_PER_DEITY = REMAINING_SHARDS / DEITY_COUNT # 9,040,928.712871287 Shards each

def load_json_file(path, default_factory):
    if os.path.exists(path):
        with open(path, "r") as f:
            try: return json.load(f)
            except json.JSONDecodeError: return default_factory()
    return default_factory()

# ─── SERVE FRONTEND INTERFACE ────────────────────────────────────────
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

# ─── SEMHAL CENTRAL SYNCHRONIZATION API ROUTES ────────────────────────
@app.route("/api/auth/register", methods=["POST"])
def proxy_register():
    data = request.json or {}
    try:
        response = requests.post(f"{SEMHAL_ECOSYSTEM_URL}/api/register", json=data, timeout=10)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({"status": "error", "message": "Semhal hub communication link timed out."}), 503

@app.route("/api/auth/login", methods=["POST"])
def proxy_login():
    data = request.json or {}
    try:
        response = requests.post(f"{SEMHAL_ECOSYSTEM_URL}/api/login", json=data, timeout=10)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({"status": "error", "message": "Semhal auth cluster down."}), 503

@app.route("/api/auth/reset", methods=["POST"])
def proxy_reset():
    data = request.json or {}
    try:
        response = requests.post(f"{SEMHAL_ECOSYSTEM_URL}/api/reset-password", json=data, timeout=10)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({"status": "error", "message": "Reset sequence pipeline failed."}), 503

@app.route("/api/ledger", methods=["GET"])
def get_ledger():
    matrix = load_json_file(MATRIX_PATH, list)
    wallet = request.args.get("wallet", "").strip()
    
    user_shards = {}
    if wallet:
        try:
            res = requests.get(f"{SEMHAL_ECOSYSTEM_URL}/api/balances?wallet={wallet}", timeout=5)
            if res.status_code == 200:
                user_shards = res.json().get("shards_inventory", {})
        except requests.exceptions.RequestException:
            pass

    for item in matrix:
        item["price_susd"] = PRICE_PER_SHARD
        item["user_owned_shards"] = user_shards.get(str(item["id"]), 0)
        
    return jsonify(matrix)

@app.route("/api/transaction", methods=["POST"])
def process_transaction():
    data = request.json or {}
    action = data.get("action", "buy").lower()
    wallet = data.get("wallet", "").strip()
    target_recipient = data.get("target_recipient", "").strip()
    amount = int(data.get("amount", 0))
    asset_id = str(data.get("asset_id", ""))
    
    if not wallet:
        return jsonify({"status": "rejected", "message": "Missing authorized public address signature."}), 400
        
    base_value = amount * PRICE_PER_SHARD

    # Synchronize transaction parameters with updated economic rules
    payload = {
        "wallet": wallet,
        "target_recipient": target_recipient,
        "action": action,
        "asset_id": asset_id,
        "amount": amount,
        "total_value_susd": base_value,
        "escrow_target": TARGET_WALLET,
        "system_meta": {
            "total_shards": TOTAL_SHARDS,
            "shards_per_deity": SHARDS_PER_DEITY,
            "sold_shards_offset": SOLD_SHARDS
        }
    }

    try:
        response = requests.post(f"{SEMHAL_ECOSYSTEM_URL}/api/settle-transaction", json=payload, timeout=12)
        semhal_res = response.json()
        
        if response.status_code != 200 or semhal_res.get("status") != "confirmed":
            return jsonify({"status": "rejected", "message": semhal_res.get("message", "Ecosystem balance verification failed.")}), 400
            
        return jsonify({
            "status": "synchronized",
            "message": f"Asset transaction settled successfully on Semhal ledger.",
            "updated_inventory_balance": semhal_res.get("new_shard_balance", 0),
            "net_total_susd": base_value
        })
    except requests.exceptions.RequestException:
        return jsonify({"status": "rejected", "message": "Cross-network transaction validation link broken."}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
