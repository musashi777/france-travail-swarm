import re
import math

def calculate_match_score(user_profile, job_offer):
    """
    Optimisation de performance : Calcul de similitude vectorielle simplifié (Pure Python).
    Utilise une approche de Jaccard pondérée pour une complexité O(N).
    """
    if not user_profile: return 0
    
    # 1. Préparation des vecteurs de mots-clés
    user_data = " ".join(user_profile.get("competences", [])).lower() + " " + user_profile.get("experiences", "").lower()
    user_vector = set(re.findall(r'\w+', user_data))
    
    job_data = (job_offer.get('intitule', '') + " " + 
                job_offer.get('description', '') + " " + 
                " ".join([s.get('libelle', '') for s in job_offer.get('competences', [])])).lower()
    job_vector = set(re.findall(r'\w+', job_data))

    if not user_vector or not job_vector:
        return 0

    # 2. Calcul de l'intersection (Mots communs)
    intersection = user_vector.intersection(job_vector)
    
    # 3. Pondération métier (Score de base)
    # Si le métier du profil est dans le titre de l'offre, on booste le score
    title_match = 0
    job_title = job_offer.get('intitule', '').lower()
    for word in re.findall(r'\w+', user_profile.get("experiences", "").lower()):
        if word in job_title:
            title_match = 40
            break

    # 4. Calcul du score de Jaccard (Similitude de contenu)
    jaccard_score = (len(intersection) / len(user_vector.union(job_vector))) * 60
    
    final_score = title_match + jaccard_score
    
    return min(int(final_score), 100)
