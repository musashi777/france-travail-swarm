import requests
from src.core.resilience import rate_limit_and_backoff

class EvenementsClient:
    """Client pour l'API Mes évènements - RECHERCHE PRÉCISE (POST /mee/evenements)."""
    
    BASE_URL = "https://api.francetravail.io/partenaire/evenements/v1/mee/evenements"

    def __init__(self, auth_manager):
        self.auth = auth_manager
        self.scope = "api_evenementsv1 evenements"
        self.token = self.auth.get_token(self.scope)

    @rate_limit_and_backoff(max_retries=3)
    def search_advanced(self, departement="13", type_ev=0, secteur=None, mots_cles=None):
        """
        Recherche avancée avec filtres combinés.
        L'ajout de mots_cles permet de filtrer les événements multisectoriels.
        """
        if not self.token: return None
        
        headers = self.auth.get_auth_header(self.token)
        headers["Content-Type"] = "application/json"
        
        params = {"page": 0, "size": 50}
        
        # Construction dynamique du body pour éviter d'envoyer des champs vides
        payload = {
            "departements": [departement]
        }
        
        if type_ev and type_ev != 0:
            payload["typeEvenement"] = type_ev
        if secteur:
            payload["secteurActivite"] = secteur
        if mots_cles:
            payload["motsCles"] = mots_cles

        return requests.post(self.BASE_URL, headers=headers, json=payload, params=params, timeout=15)
