import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "config")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "kemet_matrix.json")

def generate_kemet_matrix():
    # 1. Initialize with the Genesis 4 Core Nodes
    matrix = {
        "001": {"name": "Nun", "shards": 1000000, "tag": "Ceiling Node"},
        "002": {"name": "Horus", "shards": 500000, "tag": "Equalized"},
        "003": {"name": "Ra", "shards": 500000, "tag": "Equalized"},
        "005": {"name": "Sobek", "shards": 750000, "tag": "Fixed Point Anchor"}
    }
    
    # 2. Sequential mapping array for the remaining 97 nodes to reach 101
    deity_names = [
        # The Great Ennead & Prime Emanations (004, 006 - 015)
        "Atum", "Amun", "Mut", "Khonsu", "Shu", "Tefnut", "Geb", "Nut", "Osiris", "Isis", "Set", "Nephthys",
        # The Ogdoad Foundations (016 - 022)
        "Naunet", "Heh", "Hauhet", "Kuk", "Kauket", "Anput", "Anubis",
        # Sages, Cosmic Principles & Wisdom Vectors (023 - 045)
        "Thoth", "Ma'at", "Seshat", "Ptah", "Sekhmet", "Nefertem", "Bastet", "Hathor", "Anhur", "Taweret",
        "Bes", "Khnum", "Satet", "Anuket", "Min", "Serket", "Sobek-Ra", "Hapi", "Wadjet", "Nekhbet", "Khepri", "Kherty", "Seker",
        # The Astrological & Hour Gates (046 - 070)
        "Sopdet", "Sah", "Sopdu", "Aker", "Babi", "Wepwawet", "Meskhenet", "Renentet", "Shai", "Hu", "Sia", "Heqet",
        "Mafdet", "Pakhet", "Renenutet", "Satis", "Tjenenet", "Iunyt", "Wosret", "Hedetet", "Meretseger", "Shed", "Tutu", "Yah", "Aani",
        # Elemental & Guarding Phalanxes (071 - 101)
        "Imsety", "Duamutef", "Hapi-Canopic", "Qebehsenuef", "Maahes", "Khenty-Amentiu", "Nehebkau", "Unut", "Rem", "Shimeg",
        "Shesmu", "Sia-Ab", "Ta-Bitjet", "Tenemet", "Tpt-Rrd", "Uneg", "Wadj-Wer", "Ba-Pef", "Denwen", "Gengen-Wer",
        "Ha", "Iat", "Iusaas", "Kebechet", "Mehit", "Menhit", "Mestjet", "Meurt", "Qebaut", "Sopd", "Werethekau"
    ]
    
    # 3. Process iteration and inject standard $500 pricing model
    name_idx = 0
    for i in range(1, 102):
        node_id = f"{i:03d}"
        
        # Skip indices already secured by the Genesis deployment
        if node_id in matrix:
            matrix[node_id]["price_susd"] = 500.00
            continue
            
        if name_idx < len(deity_names):
            name = deity_names[name_idx]
            name_idx += 1
            
            # Algorithmic shard distribution based on node classification groupings
            if i <= 15:
                shards = 600000
                tag = "Prime Emanation"
            elif i <= 22:
                shards = 800000
                tag = "Ogdoad Matrix"
            elif i <= 45:
                shards = 550000
                tag = "Cosmic Vector"
            else:
                shards = 450000
                tag = "Elemental Matrix"
                
            matrix[node_id] = {
                "name": name,
                "shards": shards,
                "price_susd": 500.00,
                "tag": tag
            }

    # Sort matrix components sequentially by their structural ID
    sorted_matrix = [dict({"id": k}, **v) for k, v in sorted(matrix.items())]

    # Ensure local directory config exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(OUTPUT_PATH, "w") as f:
        json.dump(sorted_matrix, f, indent=4)
        
    print(f"🎯 Succession Complete! 101 Nodes mapped and locked down to: {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_kemet_matrix()
