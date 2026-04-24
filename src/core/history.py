import json
import os
from datetime import datetime

HISTORY_FILE = "historique_candidatures.json"

def record_application(job_offer, profile_name, action_type="Consultation"):
    """Enregistre une offre dans l'historique."""
    history = load_history()
    
    entry = {
        "id": job_offer.get('id'),
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "intitule": job_offer.get('intitule'),
        "entreprise": job_offer.get('entreprise', {}).get('nom', 'Anonyme'),
        "lieu": job_offer.get('lieuTravail', {}).get('libelle'),
        "profil_utilise": profile_name,
        "action": action_type
    }
    
    # On évite les doublons sur le même ID d'offre
    history = [h for h in history if h['id'] != entry['id']]
    history.insert(0, entry)
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history[:50], f, indent=4, ensure_ascii=False) # On garde les 50 dernières

def load_history():
    """Charge l'historique complet."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []
