import requests
from src.core.resilience import rate_limit_and_backoff

class LbbClient:
    """Client pour l'API La Bonne Boite v2."""
    
    BASE_URL = "https://api.francetravail.io/partenaire/labonneboite/v2/search"

    def __init__(self, auth_manager):
        self.auth = auth_manager
        self.scope = "api_labonneboitev2"
        self.token = self.auth.get_token(self.scope)

    @rate_limit_and_backoff(max_retries=3)
    def search_companies(self, rome_code: str, lat=None, lon=None, dist=50):
        """Trouve des entreprises à fort potentiel d'embauche."""
        if not self.token: return None
        
        headers = self.auth.get_auth_header(self.token)
        params = {"rome": rome_code}
        
        # Contrainte distance <= 200km
        safe_dist = min(int(dist), 200)
        
        if lat and lon:
            params.update({"latitude": lat, "longitude": lon, "distance": safe_dist})

        return requests.get(self.BASE_URL, headers=headers, params=params, timeout=10)
