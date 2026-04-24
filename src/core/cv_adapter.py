def generate_cv_adaptation(user_profile, job_offer):
    """
    Analyse les points communs et les manques entre le profil et l'offre.
    Génère des conseils concrets pour modifier le CV.
    """
    user_skills = [s.lower() for s in user_profile.get("competences", [])]
    job_skills = [s.get('libelle', '').lower() for s in job_offer.get('competences', [])]
    job_desc = job_offer.get('description', '').lower()

    matches = []
    suggestions = []

    # 1. Identification des compétences communes (À mettre en GRAS sur le CV)
    for js in job_skills:
        found = False
        for us in user_skills:
            if us in js or js in us:
                matches.append(js.capitalize())
                found = True
                break
        if not found:
            suggestions.append(js.capitalize())

    # 2. Analyse de la description pour trouver des "soft-skills" ou outils oubliés
    keywords = ["rigueur", "autonome", "dynamique", "haccp", "logiciel", "caisse", "anglais"]
    for kw in keywords:
        if kw in job_desc and kw not in [m.lower() for m in matches]:
            suggestions.append(kw.capitalize())

    # 3. Génération du rapport
    report = ""
    report += "[bold green]✅ À METTRE EN AVANT DANS VOTRE CV :[/bold green]\n"
    if matches:
        for m in list(set(matches))[:5]:
            report += f"   • {m} (Très demandé par cet employeur)\n"
    else:
        report += "   • [Aucun match direct, misez sur votre motivation]\n"

    report += "\n[bold yellow]⚠️ MOTS-CLÉS À RAJOUTER (Si vous les maîtrisez) :[/bold yellow]\n"
    if suggestions:
        for s in list(set(suggestions))[:5]:
            report += f"   • {s}\n"
    
    report += "\n[bold cyan]💡 CONSEIL D'ACCROCHE POUR LE HAUT DU CV :[/bold cyan]\n"
    accroche = f"\"Professionnel motivé par le poste de {job_offer.get('intitule')}, "
    if matches:
        accroche += f"je maîtrise notamment {matches[0].lower()}...\""
    else:
        accroche += f"je souhaite mettre ma polyvalence au service de {job_offer.get('entreprise', {}).get('nom')}...\""
    
    report += f"{accroche}\n"
    
    return report
