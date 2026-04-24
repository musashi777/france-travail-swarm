import json
import os

PROFILES_DIR = "profiles"

def save_profile(name, data):
    """Enregistre un profil spécifique (ex: cuisine.json)."""
    filename = os.path.join(PROFILES_DIR, f"{name.lower().replace(' ', '_')}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def list_profiles():
    """Liste tous les profils disponibles."""
    if not os.path.exists(PROFILES_DIR): return []
    return [f.replace('.json', '').replace('_', ' ').capitalize() 
            for f in os.listdir(PROFILES_DIR) if f.endswith('.json')]

def load_profile(name):
    """Charge un profil spécifique."""
    filename = os.path.join(PROFILES_DIR, f"{name.lower().replace(' ', '_')}.json")
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def delete_profile(name):
    """Supprime un profil spécifique."""
    filename = os.path.join(PROFILES_DIR, f"{name.lower().replace(' ', '_')}.json")
    if os.path.exists(filename):
        os.remove(filename)
        return True
    return False
