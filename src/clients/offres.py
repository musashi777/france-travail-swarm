import requests
from src.core.resilience import rate_limit_and_backoff

class OffresClient:
    """Client spécialisé pour l'API Offres d'emploi v2 avec robustesse améliorée."""
    
    BASE_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres"

    def __init__(self, auth_manager):
        self.auth = auth_manager
        self.scope = "api_offresdemploiv2 o2dsoffre"
        self.token = self.auth.get_token(self.scope)

    @rate_limit_and_backoff(max_retries=3)
    def search(self, mots_cles: str = None, commune: str = None, distance: int = None):
        """Récupère les offres avec stratégie de repli."""
        if not self.token: return None
        
        headers = self.auth.get_auth_header(self.token)
        params = {"range": "0-20"} # On augmente un peu la plage
        
        if mots_cles: params["motsCles"] = mots_cles
        
        # Stratégie 1 : Recherche ciblée (Commune + Distance)
        if commune:
            params["commune"] = commune
            if distance is not None:
                params["distance"] = distance

        # Debug pour identifier les problèmes d'URL
        print(f"    [Debug API] Appel Offres avec : {params}")
        
        response = requests.get(f"{self.BASE_URL}/search", headers=headers, params=params, timeout=10)
        
        # Stratégie 2 : Repli (Fallback) si 204 sur la commune précise
        if response.status_code == 204 and commune and distance is not None:
            print("    [Info] Aucun résultat précis, élargissement au département...")
            params.pop("distance", None)
            params["departement"] = commune[:2]
            response = requests.get(f"{self.BASE_URL}/search", headers=headers, params=params, timeout=10)

        return response
