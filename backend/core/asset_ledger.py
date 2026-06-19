# backend/core/asset_ledger.py

DEITY_METRICS = {}

# Tier 1: The Sovereign Peak (Absolute Maximum Price Point)
DEITY_METRICS[1] = {"name": "Nun", "total_shards": 40000, "price_susd": 11257.50}

# Solar Exception Pool (Perfect Balance, Isolated from cascading dependencies)
DEITY_METRICS[2] = {"name": "Horus", "total_shards": 500000, "price_susd": 800.00}
DEITY_METRICS[3] = {"name": "Ra", "total_shards": 500000, "price_susd": 800.00}

# Tier 1 Continued: Primordial Hierarchy
DEITY_METRICS[4] = {"name": "Atum", "total_shards": 480000, "price_susd": 780.00}
DEITY_METRICS[5] = {"name": "Sobek (The Fixed Point)", "total_shards": 450000, "price_susd": 750.00}
DEITY_METRICS[6] = {"name": "Anubis", "total_shards": 450000, "price_susd": 750.00}
DEITY_METRICS[7] = {"name": "Ammit", "total_shards": 450000, "price_susd": 750.00}
DEITY_METRICS[8] = {"name": "Apophis / Apep", "total_shards": 450000, "price_susd": 750.00}

# Tier 2: The Core Dynastic Pillars
for i in range(9, 41):
    DEITY_METRICS[i] = {"name": f"Dynastic Order Node #{i}", "total_shards": 225000, "price_susd": 550.00}

# Tier 3: Supporting & Minor Authorities
for i in range(41, 74):
    DEITY_METRICS[i] = {"name": f"Supporting Authority #{i}", "total_shards": 180000, "price_susd": 475.00}

# Tier 4: Elemental Vectors & Foundations
for i in range(74, 96):
    DEITY_METRICS[i] = {"name": f"Elemental Vector #{i}", "total_shards": 127100, "price_susd": 385.00}

for i in range(96, 102):
    DEITY_METRICS[i] = {"name": f"Foundation Layer Node #{i}", "total_shards": 60000, "price_susd": 385.00}

# Explicit Naming Mapping Integrity Checks
DEITY_METRICS[9]["name"] = "Osiris"
DEITY_METRICS[10]["name"] = "Isis"
DEITY_METRICS[11]["name"] = "Set"
DEITY_METRICS[12]["name"] = "Nephthys"
DEITY_METRICS[13]["name"] = "Thoth"
DEITY_METRICS[14]["name"] = "Ma'at"
