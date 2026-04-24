import math
import json
import os
from datetime import datetime

ALERTS_FILE = "seen_offers.json"
SEARCH_HISTORY_FILE = "search_history.json"

def calculate_gps_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance réelle en km entre deux points GPS (Haversine)."""
    if not all([lat1, lon1, lat2, lon2]): return 0.0
    R = 6371  # Rayon de la Terre
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * 
         math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def is_new_offer(offer_id):
    """Vérifie si une offre est nouvelle (jamais vue)."""
    seen = []
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, 'r') as f: seen = json.load(f)
    if offer_id in seen: return False
    seen.append(offer_id)
    with open(ALERTS_FILE, 'w') as f: json.dump(seen[-500:], f) # Garde les 500 dernières
    return True

def record_search(query, city):
    """Enregistre les paramètres de recherche."""
    history = []
    if os.path.exists(SEARCH_HISTORY_FILE):
        with open(SEARCH_HISTORY_FILE, 'r') as f: history = json.load(f)
    entry = {"query": query, "city": city, "date": datetime.now().strftime("%d/%m %H:%M")}
    # Évite les doublons identiques
    history = [h for h in history if not (h['query'] == query and h['city'] == city)]
    history.insert(0, entry)
    with open(SEARCH_HISTORY_FILE, 'w') as f: json.dump(history[:5], f)

def get_search_history():
    if os.path.exists(SEARCH_HISTORY_FILE):
        with open(SEARCH_HISTORY_FILE, 'r') as f: return json.load(f)
    return []
