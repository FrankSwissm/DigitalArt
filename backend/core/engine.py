# backend/core/engine.py

import json
import os
from typing import Dict, Any
from core.asset_ledger import DEITY_METRICS

class ArtWebEngine:
    def __init__(self):
        self.asset_registry = DEITY_METRICS
        self.user_vaults: Dict[str, Dict[int, int]] = {}
        self.tier_rules = self._load_tier_config()

    def _load_tier_config(self) -> Dict[str, Any]:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'user_tiers.json')
        with open(config_path, 'r') as file:
            return json.load(file)["tiers"]

    def process_purchase(self, user_id: str, tier: str, deity_id: int, shards: int) -> Dict[str, Any]:
        normalized_tier = tier.lower()
        if normalized_tier not in self.tier_rules:
            return {"success": False, "error": "Invalid account tier definition."}
        if deity_id not in self.asset_registry:
            return {"success": False, "error": "Asset ID not found in 101 Deity parameters."}

        asset = self.asset_registry[deity_id]
        rules = self.tier_rules[normalized_tier]

        if shards > rules["max_daily_shards_purchasable"]:
            return {"success": False, "error": "Order exceeds your daily structural tier limit."}

        base_cost = asset["price_susd"] * shards
        fee = base_cost * rules["fee_percentage"]
        cashback = base_cost * rules["cashback_multiplier"]
        final_cost = base_cost + fee - cashback

        if user_id not in self.user_vaults:
            self.user_vaults[user_id] = {}

        self.user_vaults[user_id][deity_id] = self.user_vaults[user_id].get(deity_id, 0) + shards

        return {
            "success": True,
            "user_id": user_id,
            "tier_status": normalized_tier.upper(),
            "asset_name": asset["name"],
            "shards_minted": shards,
            "base_cost_susd": base_cost,
            "fee_susd": fee,
            "cashback_awarded_susd": cashback,
            "final_invoice_amount_susd": final_cost
        }
