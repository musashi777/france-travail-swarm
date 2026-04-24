import pypdf
import re

SKILLS_LIBRARY = {
    "Restauration": ["haccp", "service", "cuisine", "encaissement", "plonge", "salle", "accueil", "barman", "serveur"],
    "Informatique": ["python", "java", "sql", "réseau", "maintenance", "linux", "windows", "support", "helpdesk", "cloud"],
    "BTP": ["maçonnerie", "lecture de plan", "sécurité", "chantier", "peinture", "électricité"],
    "Savoir-être": ["rigueur", "autonomie", "travail d'équipe", "ponctuel", "dynamique"]
}

def extract_text_from_pdf(pdf_path):
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except:
        return None

def analyze_cv_content(text):
    """Analyse le texte et GARDE le texte original pour l'adaptation."""
    if not text: return None
    
    found_skills = []
    text_lower = text.lower()
    
    for category, skills in SKILLS_LIBRARY.items():
        for skill in skills:
            if re.search(rf'\b{skill}\b', text_lower):
                found_skills.append(skill.capitalize())
                
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    return {
        "nom": lines[0] if lines else "Candidat",
        "experiences": text, # On garde TOUT le texte original ici
        "competences": list(set(found_skills)),
        "points_forts": "Expertise confirmée"
    }
