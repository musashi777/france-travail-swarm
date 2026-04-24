import requests
from src.core.resilience import rate_limit_and_backoff

class RomeClient:
    """Client pour l'API ROME 4.0 - Version v4."""
    
    BASE_URL = "https://api.francetravail.io/partenaire/rome-competences/v1/competences"

    def __init__(self, auth_manager):
        self.auth = auth_manager
        self.scope = "api_rome-v4"
        self.token = self.auth.get_token(self.scope)

    @rate_limit_and_backoff(max_retries=2)
    def search_rome_code(self, query_text: str):
        """Traduit un intitulé métier en code ROME via /search."""
        if not self.token: return None
        
        url = f"{self.BASE_URL}/search"
        headers = self.auth.get_auth_header(self.token)
        params = {"q": query_text}

        return requests.get(url, headers=headers, params=params, timeout=10)
