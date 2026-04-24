from datetime import datetime

def generate_cover_letter(user_profile, job_offer):
    """
    Génère un brouillon de lettre de motivation personnalisé.
    """
    date = datetime.now().strftime("%d/%m/%Y")
    entreprise = job_offer.get('entreprise', {}).get('nom', 'votre entreprise')
    poste = job_offer.get('intitule')
    lieu = job_offer.get('lieuTravail', {}).get('libelle')
    
    letter = f"""
Objet : Candidature au poste de {poste}

À l'attention du responsable du recrutement de {entreprise},

Actuellement à la recherche de nouvelles opportunités professionnelles sur {lieu}, c'est avec un vif intérêt que j'ai pris connaissance de votre offre pour le poste de {poste}.

Fort d'une expérience en tant que {user_profile.get('experiences', 'professionnel motivé')}, je possède des compétences en {', '.join(user_profile.get('competences', []))[:100]}... qui correspondent aux attentes de votre établissement.

Mes points forts, notamment {user_profile.get('points_forts', 'ma rigueur et mon sens du service')}, me permettront de m'intégrer rapidement à votre équipe et de contribuer au succès de {entreprise}.

Je reste à votre entière disposition pour un entretien afin de vous exposer plus en détail mes motivations.

Dans l'attente de votre réponse, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

Fait le {date},
{user_profile.get('nom')}
"""
    return letter
