import re

def extract_salary_value(salary_text):
    """
    Extrait une valeur numérique comparable d'un texte de salaire France Travail.
    Gère les formats : 'Mensuel de 1830.0 Euros', 'Horaire de 12.02 Euros', etc.
    """
    if not salary_text or not isinstance(salary_text, str):
        return 0.0
    
    # Extraction des nombres (entiers ou décimaux)
    match = re.search(r'(\d+[\.,]?\d*)', salary_text)
    if not match:
        return 0.0
    
    val = float(match.group(1).replace(',', '.'))
    
    # Normalisation : si c'est de l'horaire (ex: 12.02), on convertit en mensuel base 35h (x 151.67)
    if "horaire" in salary_text.lower():
        val = val * 151.67
        
    return val
