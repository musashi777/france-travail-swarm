import csv
from datetime import datetime

def export_to_csv(data_list, filename_prefix="recherche"):
    """
    Exporte une liste de dictionnaires en fichier CSV.
    Gère intelligemment les différents types de données (Offres ou Événements).
    """
    if not data_list:
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    
    # On extrait les clés pour l'en-tête (basé sur le premier élément)
    keys = data_list[0].keys()
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=keys, delimiter=';')
            writer.writeheader()
            writer.writerows(data_list)
        return filename
    except Exception as e:
        print(f"    [Error] Échec de l'export CSV : {e}")
        return None
