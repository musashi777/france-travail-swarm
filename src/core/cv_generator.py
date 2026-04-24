from fpdf import FPDF
from datetime import datetime

class ProfessionalCV(FPDF):
    def header(self):
        # En-tête large et clair
        self.set_font('helvetica', 'B', 24)
        self.set_text_color(33, 47, 61)
        self.cell(0, 15, self.user_name.upper(), ln=True, align='L')
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(41, 128, 185)
        self.cell(0, 10, self.target_job.upper(), ln=True, align='L')
        self.ln(5)
        self.set_draw_color(41, 128, 185)
        self.set_line_width(1)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def section_header(self, title):
        self.ln(5)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(41, 128, 185)
        self.cell(0, 8, f" {title}", ln=True, fill=True)
        self.ln(3)

def create_full_cv_pdf(user_profile, job_offer, filename="CV_Adapte.pdf"):
    """Génère un CV professionnel complet sans limitation de texte."""
    pdf = ProfessionalCV()
    pdf.user_name = user_profile.get('nom', 'Candidat')
    pdf.target_job = job_offer.get('intitule', 'Poste Visé')
    
    pdf.add_page()
    
    # 1. ACCROCHE / PROFIL
    pdf.section_header("PROFIL PROFESSIONNEL")
    pdf.set_font('helvetica', '', 11)
    pdf.set_text_color(0)
    accroche = f"Professionnel motivé par le poste de {pdf.target_job} chez {job_offer.get('entreprise', {}).get('nom')}. " \
               f"Je souhaite mettre à profit mon expérience solide et ma polyvalence pour contribuer activement au succès de votre établissement."
    pdf.multi_cell(0, 6, accroche)

    # 2. EXPÉRIENCES (LE TEXTE INTÉGRAL)
    pdf.section_header("PARCOURS ET EXPÉRIENCES")
    pdf.set_font('helvetica', '', 10)
    # On injecte l'intégralité du texte sans coupure
    pdf.multi_cell(0, 5, user_profile.get('experiences', 'Détails non fournis.'))

    # 3. COMPÉTENCES CIBLÉES
    pdf.section_header("COMPÉTENCES TECHNIQUES & SAVOIR-FAIRE")
    pdf.set_font('helvetica', '', 10)
    user_skills = [s.lower() for s in user_profile.get('competences', [])]
    job_skills = [s.get('libelle') for s in job_offer.get('competences', [])]
    
    for skill in job_skills:
        pdf.cell(10)
        status = "[X]" if any(u in skill.lower() for u in user_skills) else "[ ]"
        pdf.cell(0, 6, f"{status} {skill}", ln=True)

    # 4. INFOS COMPLÉMENTAIRES
    qualities = [q.get('libelle') for q in job_offer.get('qualitesProfessionnelles', [])]
    if qualities:
        pdf.section_header("QUALITÉS PERSONNELLES")
        pdf.set_font('helvetica', 'I', 10)
        pdf.multi_cell(0, 6, " • " + "\n • ".join(qualities))

    # Footer
    pdf.set_y(-20)
    pdf.set_font('helvetica', 'I', 8)
    pdf.set_text_color(150)
    pdf.cell(0, 10, f"Document généré pour l'offre {job_offer.get('id')} - Swarm Platform v18.0", align='R')

    pdf.output(filename)
    return filename

def get_cv_content_structure(user_profile, job_offer):
    """Structure simplifiée pour l'aperçu."""
    return {
        "nom": user_profile.get('nom'),
        "poste": job_offer.get('intitule'),
        "accroche": "Adaptation personnalisée pour " + job_offer.get('entreprise', {}).get('nom', 'N/A'),
        "competences": [s.get('libelle') for s in job_offer.get('competences', [])[:5]],
        "experience": "Contenu complet de votre CV original"
    }
