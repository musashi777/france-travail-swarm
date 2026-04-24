def calculate_match_score(user_profile, job_offer):
    """
    Algorithme de matching V3 : Intelligence Sémantique.
    Fait le lien entre les mots différents mais liés au même métier.
    """
    user_skills = [s.lower() for s in user_profile.get("competences", [])]
    user_exp = user_profile.get("experiences", "").lower()
    
    job_title = job_offer.get('intitule', '').lower()
    job_desc = job_offer.get('description', '').lower()
    job_skills = [s.get('libelle', '').lower() for s in job_offer.get('competences', [])]

    # Familles de synonymes pour la restauration
    SYNONYMES = {
        "restauration": ["snacking", "cuisine", "fast food", "snack", "salle", "restaurant", "déjeuner"],
        "polyvalent": ["équipier", "agent", "employé", "aide", "multi-technique"],
        "service": ["accueil", "relation client", "caisse", "encaissement", "plateau"],
        "haccp": ["hygiène", "sécurité alimentaire", "propreté", "nettoyage", "entretient"]
    }

    score = 0

    # 1. Matching Titre (40 pts max)
    if user_exp in job_title:
        score += 40
    else:
        # Check synonymes du métier
        for key, syns in SYNONYMES.items():
            if key in user_exp and any(s in job_title for s in syns):
                score += 30

    # 2. Matching Compétences (40 pts max)
    points_par_comp = 40 / max(len(job_skills), 1)
    for j_skill in job_skills:
        # Check direct
        if any(u_skill in j_skill for u_skill in user_skills):
            score += points_par_comp
        else:
            # Check via synonymes
            for key, syns in SYNONYMES.items():
                if key in user_skills and any(s in j_skill for s in syns):
                    score += points_par_comp * 0.8

    # 3. Bonus Description (20 pts)
    for u_skill in user_skills:
        if u_skill in job_desc:
            score += 5
        else:
            for key, syns in SYNONYMES.items():
                if key == u_skill and any(s in job_desc for s in syns):
                    score += 3

    return min(int(score), 100)
