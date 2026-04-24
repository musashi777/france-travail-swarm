from fpdf import FPDF
from datetime import datetime

class CVGenerator(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, self.user_name.upper(), ln=True, align='C')
        self.set_font('helvetica', 'I', 12)
        self.set_text_color(100)
        self.cell(0, 10, self.target_job, ln=True, align='C')
        self.ln(5)

    def section_title(self, title):
        self.set_font('helvetica', 'B', 14)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, title, ln=True, fill=True)
        self.ln(2)

def get_cv_content_structure(user_profile, job_offer):
    """
    Prépare le contenu textuel structuré pour la prévisualisation.
    """
    user_skills = user_profile.get('competences', [])
    job_skills = [s.get('libelle') for s in job_offer.get('competences', [])]
    
    # 1. Accroche
    accroche = f"Professionnel dynamique avec une expérience en tant que {user_profile.get('experiences')}. " \
               f"Maîtrisant les enjeux de {job_offer.get('intitule')}, je souhaite apporter mes compétences à {job_offer.get('entreprise', {}).get('nom')}."
    
    # 2. Compétences ciblées
    matched_skills = []
    for skill in job_skills[:8]:
        mark = "[OK]" if any(u.lower() in skill.lower() for u in user_skills) else "[+]"
        matched_skills.append(f"{mark} {skill}")

    return {
        "nom": user_profile.get('nom', 'Candidat'),
        "poste": job_offer.get('intitule'),
        "entreprise": job_offer.get('entreprise', {}).get('nom', 'N/A'),
        "accroche": accroche,
        "competences": matched_skills,
        "experience": f"Dernier poste : {user_profile.get('experiences')}"
    }

def create_full_cv_pdf(user_profile, job_offer, filename="CV_Adapte.pdf"):
    """Génère le PDF final."""
    struct = get_cv_content_structure(user_profile, job_offer)
    pdf = CVGenerator()
    pdf.user_name = struct["nom"]
    pdf.target_job = struct["poste"]
    pdf.add_page()
    
    pdf.section_title("PROFIL")
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 6, struct["accroche"])
    pdf.ln(5)

    pdf.section_title("COMPÉTENCES CLÉS")
    pdf.set_font('helvetica', '', 11)
    for skill in struct["competences"]:
        pdf.cell(5)
        pdf.cell(0, 6, f"• {skill.replace('[OK]', '').replace('[+]', '')}", ln=True)
    pdf.ln(5)

    pdf.section_title("EXPÉRIENCE PROFESSIONNELLE")
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 6, struct["experience"], ln=True)
    pdf.ln(5)

    pdf.output(filename)
    return filename
