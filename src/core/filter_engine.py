def apply_exclusions(offres, excluded_words):
    """
    Élimine les offres contenant des mots interdits dans le titre ou la description.
    """
    if not excluded_words:
        return offres
        
    filtered_list = []
    keywords = [w.strip().lower() for w in excluded_words if w.strip()]
    
    for o in offres:
        content = f"{o.get('intitule', '')} {o.get('description', '')}".lower()
        should_exclude = any(word in content for word in keywords)
        
        if not should_exclude:
            filtered_list.append(o)
            
    return filtered_list

def sort_by_salary(offres, reverse=True):
    """
    Trie les offres par salaire (décroissant par défaut).
    """
    from src.core.salary_parser import extract_salary_value
    
    return sorted(
        offres, 
        key=lambda x: extract_salary_value(x.get('salaire', {}).get('libelle', '')),
        reverse=reverse
    )
