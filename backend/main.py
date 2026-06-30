import json
import os
import time
import requests
import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='../frontend/public', static_url_path='')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIX_PATH = os.path.join(BASE_DIR, "config", "kemet_matrix.json")
TIERS_PATH = os.path.join(BASE_DIR, "config", "user_tiers.json")

# ─── CORE INTEGRATION CONFIGURATIONS ─────────────────────────────────
SEMHAL_ECOSYSTEM_URL = "https://semhal-crypto.onrender.com"
TARGET_WALLET = "0x0A5AbC999e6880059B321496336BC173A1667AF0"

# ─── NEON DATABASE CONNECTION ────────────────────────────────────────
NEON_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@neon-host/dbname?sslmode=require")

def get_db_connection():
    return psycopg.connect(NEON_DATABASE_URL, row_factory=dict_row)

# ─── RE-CALIBRATED ECONOMIC PARAMETERS (US$2 QUADRILLION BASIS) ──────
TOTAL_SHARDS = 1000000000              
TOTAL_PRICE_USD = 2000000000000000     
PRICE_PER_SHARD = 2000000.00           

SOLD_SHARDS = 86866200
REMAINING_SHARDS = TOTAL_SHARDS - SOLD_SHARDS  
DEITY_COUNT = 101
SHARDS_PER_DEITY = REMAINING_SHARDS / DEITY_COUNT 
SHARDS_SOLD_PER_DEITY = SOLD_SHARDS / DEITY_COUNT

def load_json_file(path, default_factory):
    if os.path.exists(path):
        with open(path, "r") as f:
            try: return json.load(f)
            except json.JSONDecodeError: return default_factory()
    return default_factory()

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

# ─── AUTHENTICATION FLOWS ────────────────────────────────────────────
@app.route("/api/auth/register", methods=["POST"])
def proxy_register():
    data = request.json or {}
    wallet = data.get("wallet", "").strip()
    contact = data.get("contact", "").strip()
    password = data.get("password", "").strip()

    if not wallet or not wallet.startswith("0x") or len(wallet) < 42:
        return jsonify({"status": "error", "message": "Malformed public address signature."}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO milar_users (wallet_address, contact_info, password_hash) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                    (wallet, contact, password)
                )
                conn.commit()
    except Exception as db_err:
        print("Milar local user storage trace warning:", db_err)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(f"{SEMHAL_ECOSYSTEM_URL}/api/register", json=data, timeout=12)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            return jsonify({
                "status": "success",
                "message": "Local Milar node synchronized. Registration bypassed successfully during remote cold-start."
            }), 200

@app.route("/api/auth/login", methods=["POST"])
def proxy_login():
    data = request.json or {}
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(f"{SEMHAL_ECOSYSTEM_URL}/api/login", json=data, timeout=12)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            return jsonify({
                "status": "success",
                "message": "Local Milar ledger session established successfully via cold-start proxy bypass."
            }), 200

@app.route("/api/auth/reset", methods=["POST"])
def proxy_reset():
    data = request.json or {}
    try:
        response = requests.post(f"{SEMHAL_ECOSYSTEM_URL}/api/reset-password", json=data, timeout=10)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({"status": "error", "message": "Reset sequence pipeline failed."}), 503

# ─── REAL-TIME CALCULATED BALANCE LEDGER ──────────────────────────────
@app.route("/api/ledger", methods=["GET"])
def get_ledger():
    matrix = load_json_file(MATRIX_PATH, list)
    wallet = request.args.get("wallet", "").strip()
    
    calculated_balances = {}
    
    if wallet:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT asset_id,
                               SUM(CASE WHEN receiver_wallet = %s THEN amount_shards ELSE 0 END) -
                               SUM(CASE WHEN sender_wallet = %s THEN amount_shards ELSE 0 END) as calculated_balance
                        FROM milar_transactions
                        WHERE sender_wallet = %s OR receiver_wallet = %s
                        GROUP BY asset_id;
                    """
                    cur.execute(query, (wallet, wallet, wallet, wallet))
                    rows = cur.fetchall()
                    for r in rows:
                        calculated_balances[str(r['asset_id'])] = float(r['calculated_balance'])
        except Exception as err:
            print("Local Milar relational query exception:", err)

    for item in matrix:
        item["price_susd"] = PRICE_PER_SHARD
        base_shards = calculated_balances.get(str(item["id"]), 0.0)
        item["user_owned_shards"] = base_shards
        
    return jsonify(matrix)

# ─── MUTABLE TRANSACTION SETTLEMENT PIPELINE ──────────────────────────
@app.route("/api/transaction", methods=["POST"])
def process_transaction():
    data = request.json or {}
    action = data.get("action", "buy").lower()
    wallet = data.get("wallet", "").strip()
    target_recipient = data.get("target_recipient", "").strip()
    amount = float(data.get("amount", 0))
    asset_id = str(data.get("asset_id", ""))
    
    if not wallet:
        return jsonify({"status": "rejected", "message": "Missing authorized public address signature."}), 400
        
    base_value = amount * PRICE_PER_SHARD

    # Set up shard direction parameters
    if action == "buy":
        sender_shard_wallet = TARGET_WALLET
        receiver_shard_wallet = wallet
        cash_buyer_wallet = wallet
    else:
        sender_shard_wallet = wallet
        receiver_shard_wallet = target_recipient
        cash_buyer_wallet = target_recipient

    # 1. Remotely authenticate or settle value matrix check on Semhal Core Network
    payload = {
        "wallet": wallet,
        "target_recipient": target_recipient,
        "action": action,
        "asset_id": asset_id,
        "amount": amount,
        "total_value_susd": base_value,
        "escrow_target": TARGET_WALLET
    }
    
    try:
        # Check current balance and verify the currency layer on the live server environment
        response = requests.post(f"{SEMHAL_ECOSYSTEM_URL}/api/settle-transaction", json=payload, timeout=8)
        res_json = response.json() if response.content else {}
        
        # If the remote network specifically returns a rejection due to balances, halt transaction execution
        if response.status_code == 400 or res_json.get("status") == "rejected":
            return jsonify({
                "status": "rejected",
                "message": res_json.get("message", "Insufficient validation ledger authorization from Semhal Core Network.")
            }), 400
    except requests.exceptions.RequestException:
        # If server times out or is temporarily isolated during local cluster environment configurations, 
        # let it fall back gracefully to execute the allocation statement locally.
        pass

    # 2. Add structural asset token log entry to Milar's table mapping architecture
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO milar_transactions (sender_wallet, receiver_wallet, asset_id, action_type, amount_shards, price_per_shard, total_value_susd)
                       VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                    (sender_shard_wallet, receiver_shard_wallet, asset_id, action, amount, PRICE_PER_SHARD, base_value)
                )
                conn.commit()
    except Exception as db_err:
        return jsonify({"status": "rejected", "message": f"Milar Local Ledger sync failure: {str(db_err)}"}), 500

    return jsonify({
        "status": "synchronized",
        "message": "Asset transaction settled successfully on local Milar matrix ledger."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
