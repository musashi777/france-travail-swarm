import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()

class FranceTravailAuth:
    """
    Gestionnaire d'identité avec mise en cache locale des jetons.
    Économise les appels API et accélère le démarrage.
    """
    
    TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
    CACHE_FILE = ".ft_token_cache"

    def __init__(self):
        self.client_id = os.getenv("FT_CLIENT_ID")
        self.client_secret = os.getenv("FT_CLIENT_SECRET")

    def get_token(self, scopes: str):
        """Récupère un jeton valide (depuis le cache ou via API)."""
        cache = self._read_cache()
        
        # Si le jeton pour ce scope existe et est encore valide (marge de 60s)
        if cache and scopes in cache:
            token_data = cache[scopes]
            if token_data['expires_at'] > time.time() + 60:
                return token_data['access_token']

        # Sinon, on demande un nouveau jeton
        return self._fetch_new_token(scopes)

    def _fetch_new_token(self, scopes: str):
        full_scope = f"application_{self.client_id} {scopes}"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": full_scope
        }
        
        try:
            response = requests.post(self.TOKEN_URL, data=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                expires_in = data.get("expires_in", 1499)
                
                # Mise à jour du cache
                self._write_cache(scopes, access_token, expires_in)
                return access_token
            return None
        except:
            return None

    def _read_cache(self):
        if os.path.exists(self.CACHE_FILE):
            try:
                with open(self.CACHE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _write_cache(self, scopes, token, expires_in):
        cache = self._read_cache()
        cache[scopes] = {
            "access_token": token,
            "expires_at": time.time() + expires_in
        }
        with open(self.CACHE_FILE, 'w') as f:
            json.dump(cache, f)

    def get_auth_header(self, token):
        return {
            "Authorization": f"Bearer {token}",
            "User-Agent": "MonApplication/1.0",
            "Accept": "application/json"
        }
