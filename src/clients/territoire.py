import requests
from src.core.resilience import rate_limit_and_backoff

class TerritoireClient:
    """Client pour l'API Informations sur un territoire v2."""
    
    BASE_URL = "https://api.francetravail.io/partenaire/infoterritoire/v1/territoire"

    def __init__(self, auth_manager):
        self.auth = auth_manager
        # Scope validé pour la version 2026
        self.scope = "api_infoterritoire-v2"
        self.token = self.auth.get_token(self.scope)

    @rate_limit_and_backoff(max_retries=3)
    def get_dynamisme(self, code_postal: str):
        """Récupère le score de dynamisme économique d'une zone."""
        if not self.token: return None
        
        url = f"{self.BASE_URL}/search"
        headers = self.auth.get_auth_header(self.token)
        params = {"codeZone": code_postal}

        return requests.get(url, headers=headers, params=params, timeout=10)
