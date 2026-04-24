import sys
import os
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import print as rprint

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports des services
from src.auth.manager import FranceTravailAuth
from src.clients.evenements import EvenementsClient
from src.clients.offres import OffresClient
from src.clients.territoire import TerritoireClient

# Imports du coeur IA
from src.core.geo import get_insee_code
from src.core.profile import load_profile, save_profile, list_profiles, delete_profile
from src.core.matching import calculate_match_score
from src.core.letter import generate_cover_letter
from src.core.cv_adapter import generate_cv_adaptation
from src.core.cv_generator import create_full_cv_pdf, get_cv_content_structure
from src.core.intelligence import record_search, get_search_history, is_new_offer
from src.core.history import record_application, load_history
from src.core.cv_processor import extract_text_from_pdf, analyze_cv_content

console = Console()

class SwarmTerminal:
    def __init__(self):
        with console.status("[bold blue]Initialisation de la Station Unifiée...", spinner="dots"):
            self.auth = FranceTravailAuth()
            self.events_api = EvenementsClient(self.auth)
            self.jobs_api = OffresClient(self.auth)
            self.territory_api = TerritoireClient(self.auth)
            self.active_profile = None
            self.active_profile_name = "Aucun"

    def welcome_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')
        rprint(Panel.fit(
            f"[bold cyan]🚀 SWARM STATION v16.0[/bold cyan]\n"
            f"[bold yellow]PROFIL ACTIF : {self.active_profile_name}[/bold yellow] | [bold green]Connecté FT API[/bold green]",
            border_style="bright_blue", padding=(0, 4)
        ))

    def main_menu(self):
        while True:
            self.welcome_screen()
            choice = questionary.select(
                "Que voulez-vous faire ?",
                choices=[
                    "💼 RECHERCHER UN EMPLOI (Offres + Matching)",
                    "📅 TROUVER UN ÉVÉNEMENT (Job Datings)",
                    "👤 GÉRER MES PROFILS (CV & Compétences)",
                    "📜 VOIR MON HISTORIQUE / RECHERCHES",
                    "🚪 QUITTER"
                ]
            ).ask()

            if "EMPLOI" in choice: self.ui_jobs()
            elif "ÉVÉNEMENT" in choice: self.ui_events()
            elif "PROFILS" in choice: self.ui_profiles()
            elif "HISTORIQUE" in choice: self.ui_history_hub()
            else: break

    # --- SOUS-MENUS PRINCIPAUX ---

    def ui_profiles(self):
        while True:
            self.welcome_screen()
            profiles = list_profiles()
            act = questionary.select("Gestion des Profils :", choices=[
                "✅ Activer un profil", "➕ Créer (Manuel ou PDF)", "📝 Modifier l'actif", "🗑️ Supprimer", "⬅️ Retour"
            ]).ask()

            if "Retour" in act: break
            elif "Activer" in act:
                if profiles:
                    name = questionary.select("Choisir :", choices=profiles).ask()
                    self.active_profile, self.active_profile_name = load_profile(name), name
                break
            elif "Créer" in act:
                self.ui_create_profile()
                break
            elif "Modifier" in act:
                if self.active_profile: self.ui_edit_profile()
            elif "Supprimer" in act:
                if profiles:
                    name = questionary.select("Supprimer :", choices=profiles).ask()
                    if questionary.confirm("Confirmer la suppression ?").ask():
                        delete_profile(name)
                        if self.active_profile_name == name:
                            self.active_profile, self.active_profile_name = None, "Aucun"

    def ui_jobs(self):
        query = questionary.text("Poste recherché :", default=self.active_profile.get('experiences', '') if self.active_profile else "Polyvalent").ask()
        ville = questionary.text("Ville :", default="Marseille").ask()
        dist = int(questionary.select("Rayon :", choices=[
            questionary.Choice("5 km", 5), questionary.Choice("15 km", 15), questionary.Choice("50 km", 50)
        ]).ask())
        
        record_search(query, ville)
        insee = get_insee_code(ville)
        
        with console.status(f"[bold blue]Analyse Swarm pour {query}..."):
            res = self.jobs_api.search(mots_cles=query, commune=insee, distance=dist)

        if res and res.status_code in [200, 206]:
            self.browse_offres(res.json().get('resultats', []))
        else:
            rprint("[yellow]Aucune offre trouvée avec ces critères.[/yellow]")
            questionary.press_any_key_to_continue().ask()

    def ui_history_hub(self):
        self.welcome_screen()
        history = load_history()
        if history:
            table = Table(title="DERNIÈRES ACTIONS", show_lines=True)
            table.add_column("DATE"); table.add_column("ENTREPRISE"); table.add_column("ACTION", style="cyan")
            for h in history[:10]: table.add_row(h['date'], h['entreprise'], h['action'])
            console.print(table)
        else:
            rprint("[italic]Aucun historique.[/italic]")
        questionary.press_any_key_to_continue().ask()

    # --- LOGIQUE DÉTAILLÉE ---

    def browse_offres(self, offres):
        page, per_page = 0, 7
        while True:
            self.welcome_screen()
            start, end = page * per_page, (page + 1) * per_page
            batch = offres[start:end]
            
            choices = []
            for i, o in enumerate(batch):
                score = f"[{calculate_match_score(self.active_profile, o)}%] " if self.active_profile else ""
                tag = "[NEW] " if is_new_offer(o.get('id')) else ""
                choices.append(questionary.Choice(title=f"{tag}{score}{o.get('intitule')}", value=start+i))
            
            if end < len(offres): choices.append(questionary.Choice(title="➡️ SUIVANT", value="next"))
            if page > 0: choices.append(questionary.Choice(title="⬅️ PRÉCÉDENT", value="prev"))
            choices.append(questionary.Choice(title="🏁 RETOUR", value="back"))

            idx = questionary.select("Choisissez une offre :", choices=choices).ask()
            if idx == "next": page += 1
            elif idx == "prev": page -= 1
            elif idx == "back": break
            else: self.display_job_detail(offres[idx])

    def display_job_detail(self, o):
        self.welcome_screen()
        cp = o.get('lieuTravail', {}).get('codePostal')
        
        # 1. Analyse Territoriale (Mission Initiale)
        with console.status("[italic]Analyse territoriale..."):
            res_t = self.territory_api.get_dynamisme(cp) if cp else None
        dyn_text = "[bold green]Zone Dynamique[/bold green]" if res_t and res_t.status_code == 200 else "[white]N/A[/white]"

        detail = Text()
        detail.append(f"\n🌍 TERRITOIRE : {dyn_text} ({cp})\n", style="italic")
        if self.active_profile:
            detail.append(f"🎯 MATCHING   : {calculate_match_score(self.active_profile, o)}%\n", style="bold magenta")
        detail.append(f"🏢 ENTREPRISE : {o.get('entreprise', {}).get('nom')}\n", style="bold green")
        detail.append(f"📄 CONTRAT    : {o.get('typeContratLibelle')}\n")
        detail.append(f"\n📝 DESCRIPTION :\n{o.get('description', 'N/A')[:500]}...\n")
        
        rprint(Panel(detail, title=f"[bold white]{o.get('intitule')}[/bold white]", border_style="cyan"))
        
        act = questionary.select("Action :", choices=["📄 GÉNÉRER DOSSIER CV+LETTRE", "🌍 VOIR MAPS", "⬅️ RETOUR"]).ask()
        if "DOSSIER" in act:
            if self.active_profile:
                self.ui_generate_dossier(o)
            else:
                rprint("[red]Activez un profil pour cette action.[/red]")
                questionary.press_any_key_to_continue().ask()
        elif "MAPS" in act:
            rprint(f"\nLien : https://www.google.com/maps/search/{o.get('lieuTravail', {}).get('libelle')}")
            questionary.press_any_key_to_continue().ask()

    def ui_generate_dossier(self, o):
        struct = get_cv_content_structure(self.active_profile, o)
        self.welcome_screen()
        rprint(Panel(f"Accroche : {struct['accroche']}\nCompétences : {', '.join(struct['competences'])}", title="👁️ APERÇU DU DOSSIER"))
        
        if questionary.confirm("Confirmer l'export PDF ?").ask():
            fname = f"CV_{o.get('id')}.pdf"
            create_full_cv_pdf(self.active_profile, o, fname)
            rprint(Panel(generate_cover_letter(self.active_profile, o), title="LETTRE GÉNÉRÉE"))
            rprint(f"[bold green]✅ Fichiers créés : {fname} + Lettre affichée ci-dessus.[/bold green]")
            record_application(o, self.active_profile_name, "Dossier Complet Généré")
            questionary.press_any_key_to_continue().ask()

    def ui_create_profile(self):
        method = questionary.select("Méthode :", choices=["📄 Importer un CV PDF", "⌨️ Saisie Manuelle"]).ask()
        name = questionary.text("Nom du métier (ex: Serveur) :").ask()
        data = {"nom": "Candidat", "competences": [], "experiences": name}
        if "CV" in method:
            path = questionary.text("Chemin du PDF :").ask()
            if os.path.exists(path):
                text = extract_text_from_pdf(path)
                cv_data = analyze_cv_content(text)
                if cv_data: data.update(cv_data)
        save_profile(name, data); self.active_profile, self.active_profile_name = data, name

    def ui_edit_profile(self):
        self.active_profile['nom'] = questionary.text("Nom :", default=self.active_profile.get('nom')).ask()
        self.active_profile['experiences'] = questionary.text("Métier :", default=self.active_profile.get('experiences')).ask()
        comps = questionary.text("Compétences (virgule) :", default=",".join(self.active_profile.get('competences'))).ask()
        self.active_profile['competences'] = [c.strip() for c in comps.split(',') if c.strip()]
        save_profile(self.active_profile_name, self.active_profile)

    def ui_events(self):
        q = questionary.text("Thème :", default="Restauration").ask()
        v = questionary.text("Ville :", default="Marseille").ask()
        insee = get_insee_code(v)
        with console.status("[bold cyan]Recherche d'événements..."):
            res = self.events_api.search_advanced(departement=insee[:2], mots_cles=q)
        if res and res.status_code == 200:
            events = res.json().get('content', [])
            table = Table(title=f"ÉVÉNEMENTS : {q.upper()}", show_lines=True)
            table.add_column("DATE"); table.add_column("TITRE"); table.add_column("VILLE")
            for ev in events[:10]: table.add_row(ev.get('dateEvenement', '').split('T')[0], ev.get('titre'), ev.get('ville'))
            console.print(table)
        questionary.press_any_key_to_continue().ask()

if __name__ == "__main__":
    try: SwarmTerminal().main_menu()
    except KeyboardInterrupt: pass
