def get_insee_code(city_name: str) -> str:
    """
    Simule une recherche de code INSEE à partir du nom de la ville.
    Dans une version pro, on pourrait appeler l'API de l'IGN ou de l'INSEE.
    """
    mapping = {
        "marseille": "13201",
        "aubagne": "13008",
        "paris": "75056",
        "lyon": "69123",
        "nice": "06088",
        "toulouse": "31555",
        "bordeaux": "33063",
        "nantes": "44109",
        "strasbourg": "67482",
        "montpellier": "34172",
        "lille": "59350"
    }
    return mapping.get(city_name.lower(), "13201") # Marseille par défaut si non trouvé
