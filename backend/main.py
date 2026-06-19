import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIX_PATH = os.path.join(BASE_DIR, "config", "kemet_matrix.json")
TIERS_PATH = os.path.join(BASE_DIR, "config", "user_tiers.json")
INVENTORY_PATH = os.path.join(BASE_DIR, "config", "user_inventories.json")

# ─── UPGRADED SYSTEM PARAMETERS ──────────────────────────────────────
TARGET_WALLET = "0xc9cx19b9f02783c68d5fde432005539e9424e228"
TOTAL_POOL_SHARDS = 100000000
TOTAL_POOL_VALUE_SUSD = 50000000000.00
PRICE_PER_SHARD = 500.00

INITIAL_CAPITAL_VAULT = 10000000000.00
DEDUCTION_AMOUNT = 7917350426.6
ECOSYSTEM_RESERVE = INITIAL_CAPITAL_VAULT - DEDUCTION_AMOUNT  # 2,082,649,573.40

def load_json_file(path, default_factory):
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default_factory()
    return default_factory()

def save_json_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def get_user_shard_balance(username, asset_id):
    inventories = load_json_file(INVENTORY_PATH, dict)
    user_records = inventories.get(username, {})
    return user_records.get(str(asset_id), 0)

def modify_user_shard_balance(inventories, username, asset_id, delta):
    if username not in inventories:
        inventories[username] = {}
        
    current_balance = inventories[username].get(str(asset_id), 0)
    new_balance = current_balance + delta
    
    if new_balance <= 0:
        inventories[username].pop(str(asset_id), None)
        new_balance = 0
    else:
        inventories[username][str(asset_id)] = new_balance
        
    return new_balance

@app.route("/api/tiers", methods=["GET"])
def get_tiers():
    return jsonify(load_json_file(TIERS_PATH, dict))

@app.route("/api/ledger", methods=["GET"])
def get_ledger():
    matrix = load_json_file(MATRIX_PATH, list)
    active_user = request.args.get("user", "User_Alpha").strip()
    
    for item in matrix:
        item["price_susd"] = PRICE_PER_SHARD
        item["user_owned_shards"] = get_user_shard_balance(active_user, item["id"])
        
    return jsonify(matrix)

@app.route("/api/transaction", methods=["POST"])
def process_transaction():
    data = request.json or {}
    action = data.get("action", "buy").lower()
    username = data.get("user", "User_Alpha").strip()
    target_recipient = data.get("target_recipient", "").strip()
    tier = data.get("tier", "Primary")
    amount = int(data.get("amount", 0))
    asset_id = str(data.get("asset_id", ""))
    
    if amount <= 0:
        return jsonify({"status": "rejected", "message": "Quantity must be greater than zero."}), 400
        
    matrix = load_json_file(MATRIX_PATH, list)
    tiers = load_json_file(TIERS_PATH, dict)
    
    asset = next((item for item in matrix if str(item["id"]) == asset_id), None)
    if not asset:
        return jsonify({"status": "rejected", "message": "Target asset entry not found."}), 404
        
    tier_rules = tiers.get("tiers", {}).get(tier, {"fee_percent": 2.0, "cashback_percent": 0.0})
    fee_factor = tier_rules.get("fee_percent", 2.0) / 100.0
    
    base_value = amount * PRICE_PER_SHARD
    inventories = load_json_file(INVENTORY_PATH, dict)
    current_holdings = inventories.get(username, {}).get(asset_id, 0)
    
    if action == "buy":
        fee_factor_cb = tier_rules.get("cashback_percent", 0.0) / 100.0
        computed_fee = base_value * fee_factor
        computed_cashback = base_value * fee_factor_cb
        net_total = base_value + computed_fee - computed_cashback
        
        updated_bal = modify_user_shard_balance(inventories, username, asset_id, amount)
        save_json_file(INVENTORY_PATH, inventories)
        message = f"Profile {username} acquired {amount} shards."
        
    elif action == "sell":
        VALID_USERS = ["User_Alpha", "User_Beta", "User_Gamma"]
        if not target_recipient or target_recipient not in VALID_USERS:
            return jsonify({"status": "rejected", "message": f"Invalid recipient configuration mapping."}), 400
            
        if target_recipient == username:
            return jsonify({"status": "rejected", "message": "Loopback transfers blocked."}), 400
            
        if current_holdings < amount:
            return jsonify({"status": "rejected", "message": f"Insufficient balance. {username} only holds {current_holdings} shards."}), 400
            
        computed_fee = base_value * fee_factor
        net_total = base_value - computed_fee
        
        # Cross-account asset swap execution
        updated_bal = modify_user_shard_balance(inventories, username, asset_id, -amount)
        modify_user_shard_balance(inventories, target_recipient, asset_id, amount)
        
        save_json_file(INVENTORY_PATH, inventories)
        message = f"P2P Swap Complete: {amount} Shards transferred from {username} to {target_recipient}."
        
    else:
        return jsonify({"status": "rejected", "message": "Unknown processing operation parameter."}), 400
        
    return jsonify({
        "status": "synchronized",
        "message": message,
        "action_executed": action,
        "user": username,
        "target_recipient": target_recipient,
        "tier_applied": tier,
        "base_value_safeguard": base_value,
        "net_total_susd": net_total,
        "updated_inventory_balance": updated_bal,
        "semhal_target_contract": TARGET_WALLET,
        "system_vault_reserve_susd": ECOSYSTEM_RESERVE
    })

if __name__ == "__main__":
    print(f"🚀 Upgraded Matrix Online: {TOTAL_POOL_SHARDS:,} Shards | Value Cap: ${TOTAL_POOL_VALUE_SUSD:,.2f} SUSD")
    app.run(host="0.0.0.0", port=8000, debug=True)
