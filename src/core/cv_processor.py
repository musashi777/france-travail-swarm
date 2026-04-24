import pypdf
import re

# Dictionnaire de référence pour l'extraction intelligente
SKILLS_LIBRARY = {
    "Restauration": ["haccp", "service", "cuisine", "encaissement", "plonge", "salle", "accueil", "barman", "serveur"],
    "Informatique": ["python", "java", "sql", "réseau", "maintenance", "linux", "windows", "support", "helpdesk", "cloud"],
    "BTP": ["maçonnerie", "lecture de plan", "sécurité", "chantier", "peinture", "électricité"],
    "Savoir-être": ["rigueur", "autonomie", "travail d'équipe", "ponctuel", "dynamique"]
}

def extract_text_from_pdf(pdf_path):
    """Extrait tout le texte d'un fichier PDF."""
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Erreur lecture PDF : {e}")
        return None

def analyze_cv_content(text):
    """Analyse le texte pour extraire le profil type."""
    if not text: return None
    
    found_skills = []
    text_lower = text.lower()
    
    # Extraction des compétences par matching de dictionnaire
    for category, skills in SKILLS_LIBRARY.items():
        for skill in skills:
            if re.search(rf'\b{skill}\b', text_lower):
                found_skills.append(skill.capitalize())
                
    # Tentative d'extraction de l'intitulé de poste (souvent en haut du CV)
    # On prend la première ligne non vide pour le test
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    potential_job = lines[0] if lines else "Candidat"
    
    return {
        "nom": "Extrait du CV",
        "experiences": potential_job,
        "competences": list(set(found_skills)),
        "points_forts": "Extrait automatiquement"
    }
