import time
import random
from functools import wraps
import requests

def rate_limit_and_backoff(max_retries=3):
    """
    Décorateur modulaire pour gérer la résilience des appels API.
    Implémente un backoff exponentiel pour les erreurs HTTP 429.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    response = func(*args, **kwargs)
                    if response is None:
                        return None
                        
                    # Gestion du Rate Limiting
                    if response.status_code == 429:
                        wait = (2 ** retries) + random.uniform(0, 1)
                        print(f"    [Resilience] 429 sur {func.__name__}. Attente {wait:.1f}s...")
                        time.sleep(wait)
                        retries += 1
                        continue
                        
                    return response
                except requests.exceptions.RequestException as e:
                    print(f"    [Error] Exception réseau sur {func.__name__} : {e}")
                    retries += 1
                    time.sleep(1)
            return None
        return wrapper
    return decorator
