import sys
import os
import questionary
import math
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import print as rprint

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth.manager import FranceTravailAuth
from src.clients.evenements import EvenementsClient
from src.clients.offres import OffresClient
from src.clients.territoire import TerritoireClient
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

class SwarmStation:
    def __init__(self):
        with console.status("[bold blue]Initialisation...", spinner="dots"):
            self.auth = FranceTravailAuth()
            self.events_api = EvenementsClient(self.auth)
            self.jobs_api = OffresClient(self.auth)
            self.territory_api = TerritoireClient(self.auth)
            self.active_profile = None
            self.active_profile_name = "Aucun"

    def welcome_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')
        rprint(Panel.fit(
            f"[bold cyan]🚀 SWARM STATION v18.0[/bold cyan]\n"
            f"[bold yellow]Profil Actif : {self.active_profile_name}[/bold yellow]",
            border_style="bright_blue"
        ))

    def main_menu(self):
        while True:
            self.welcome_screen()
            choice = questionary.select(
                "Menu :",
                choices=["💼 RECHERCHE D'EMPLOI", "📅 ÉVÉNEMENTS", "👤 GÉRER MES PROFILS", "📜 HISTORIQUE", "🚪 QUITTER"]
            ).ask()
            if "EMPLOI" in choice: self.ui_jobs()
            elif "ÉVÉNEMENT" in choice: self.ui_events()
            elif "PROFILS" in choice: self.ui_profiles()
            elif "HISTORIQUE" in choice: self.ui_history()
            else: break

    def ui_jobs(self):
        query = questionary.text("Métier :", default=self.active_profile.get('experiences', '') if self.active_profile else "Polyvalent").ask()
        ville = questionary.text("Ville :", default="Marseille").ask()
        dist = int(questionary.select("Rayon :", choices=[questionary.Choice("5 km", 5), questionary.Choice("20 km", 20)]).ask())
        insee = get_insee_code(ville)
        with console.status("[bold blue]Recherche..."):
            res = self.jobs_api.search(mots_cles=query, commune=insee, distance=dist)
        if res and res.status_code in [200, 206]:
            self.browse_offres(res.json().get('resultats', []), ville)
        else:
            rprint("[yellow]Aucune offre.[/yellow]"); questionary.press_any_key_to_continue().ask()

    def browse_offres(self, offres, search_city):
        page, per_page = 0, 7
        total_pages = math.ceil(len(offres) / per_page)
        while True:
            self.welcome_screen()
            start, end = page * per_page, (page + 1) * per_page
            batch = offres[start:end]
            choices = []
            for i, o in enumerate(batch):
                score = f"[{calculate_match_score(self.active_profile, o)}%] " if self.active_profile else ""
                choices.append(questionary.Choice(title=f"{score}{o.get('intitule')}", value=start+i))
            if end < len(offres): choices.append(questionary.Choice(title="➡️ SUIVANT", value="next"))
            if page > 0: choices.append(questionary.Choice(title="⬅️ PRÉCÉDENT", value="prev"))
            choices.append(questionary.Choice(title="🏁 RETOUR", value="back"))
            idx = questionary.select(f"Offres (Page {page + 1} / {total_pages}) :", choices=choices).ask()
            if idx == "next": page += 1
            elif idx == "prev": page -= 1
            elif idx == "back": break
            else: self.display_job_detail(offres[idx])

    def display_job_detail(self, o):
        """Affiche l'intégralité de l'offre sans coupure."""
        while True:
            self.welcome_screen()
            cp = o.get('lieuTravail', {}).get('codePostal')
            lat = o.get('lieuTravail', {}).get('latitude', 'N/A')
            lon = o.get('lieuTravail', {}).get('longitude', 'N/A')
            
            detail = Text()
            detail.append(f"📡 GPS: {lat}, {lon} | 🌍 CP: {cp}\n", style="bold yellow")
            if self.active_profile:
                detail.append(f"🎯 MATCHING : {calculate_match_score(self.active_profile, o)}%\n", style="bold magenta")
            detail.append(f"🏢 ENTREPRISE : {o.get('entreprise', {}).get('nom')}\n", style="bold green")
            detail.append(f"📄 CONTRAT    : {o.get('typeContratLibelle')} ({o.get('natureContrat')})\n")
            detail.append(f"💰 SALAIRE    : {o.get('salaire', {}).get('libelle', 'Non précisé')}\n")
            
            detail.append(f"\n[bold underline]📝 DESCRIPTION COMPLÈTE DE L'OFFRE :[/bold underline]\n\n")
            detail.append(o.get('description', 'N/A'))
            
            # Ajout des compétences et qualités si présentes
            comps = o.get('competences', [])
            if comps:
                detail.append(f"\n\n[bold underline]✅ COMPÉTENCES REQUISES :[/bold underline]\n")
                for c in comps: detail.append(f" • {c.get('libelle')}\n")
            
            qualites = o.get('qualitesProfessionnelles', [])
            if qualites:
                detail.append(f"\n[bold underline]🌟 QUALITÉS RECHERCHÉES :[/bold underline]\n")
                for q in qualites: detail.append(f" • {q.get('libelle')}\n")

            rprint(Panel(detail, title=f"[bold white]{o.get('intitule')}[/bold white]", border_style="cyan"))
            
            act = questionary.select("Actions :", choices=[
                "📄 GÉNÉRER DOSSIER CV (PDF)", "🌍 VOIR MAPS", "📝 APERÇU ADAPTATION", "⬅️ RETOUR"
            ]).ask()

            if "RETOUR" in act: break
            elif "MAPS" in act:
                rprint(f"\nLien : https://www.google.com/maps/search/{lat},{lon}")
                questionary.press_any_key_to_continue().ask()
            elif "APERÇU" in act:
                if self.active_profile:
                    rprint(Panel(generate_cv_adaptation(self.active_profile, o), title="COACHING CV"))
                else: rprint("[red]Activez un profil.[/red]")
                questionary.press_any_key_to_continue().ask()
            elif "CV" in act:
                if self.active_profile: self.ui_generate_cv(o)
                else: rprint("[red]Activez un profil.[/red]"); questionary.press_any_key_to_continue().ask()

    def ui_generate_cv(self, o):
        struct = get_cv_content_structure(self.active_profile, o)
        self.welcome_screen()
        rprint(Panel(f"Accroche : {struct['accroche']}\nCompétences : {', '.join(struct['competences'][:5])}", title="👁️ APERÇU"))
        if questionary.confirm("Voulez-vous générer le PDF final ?").ask():
            path = f"candidatures/CV_{o.get('id')}.pdf"
            create_full_cv_pdf(self.active_profile, o, path)
            rprint(Panel(f"[bold green]✅ CV GÉNÉRÉ ![/bold green]\n📍 {os.path.abspath(path)}", border_style="green"))
            record_application(o, self.active_profile_name, "Dossier PDF")
            questionary.press_any_key_to_continue().ask()

    def ui_profiles(self):
        profiles = list_profiles()
        act = questionary.select("Profils :", choices=["✅ Activer", "➕ Créer", "🗑️ Supprimer", "⬅️ Retour"]).ask()
        if "Activer" in act and profiles:
            name = questionary.select("Lequel ?", choices=profiles).ask()
            self.active_profile, self.active_profile_name = load_profile(name), name
        elif "Créer" in act:
            name = questionary.text("Métier :").ask()
            method = questionary.select("Source :", choices=["📄 PDF", "⌨️ Manuel"]).ask()
            data = {"nom": "Candidat", "competences": [], "experiences": name}
            if "PDF" in method:
                path = questionary.text("Chemin du PDF :").ask()
                if os.path.exists(path): data.update(analyze_cv_content(extract_text_from_pdf(path)))
            save_profile(name, data); self.active_profile, self.active_profile_name = data, name
        elif "Supprimer" in act and profiles:
            name = questionary.select("Lequel ?", choices=profiles).ask()
            if questionary.confirm("Sûr ?").ask(): delete_profile(name)

    def ui_history(self):
        history = load_history()
        if history:
            table = Table(title="HISTORIQUE", show_lines=True)
            table.add_column("DATE"); table.add_column("ENTREPRISE"); table.add_column("ACTION")
            for h in history[:10]: table.add_row(h['date'], h['entreprise'], h['action'])
            console.print(table)
        questionary.press_any_key_to_continue().ask()

    def ui_events(self):
        q = questionary.text("Thème :", default="Restauration").ask()
        v = questionary.text("Ville :", default="Marseille").ask()
        insee = get_insee_code(v)
        with console.status("[bold cyan]Recherche..."):
            res = self.events_api.search_advanced(departement=insee[:2], mots_cles=q)
        if res and res.status_code == 200:
            events = res.json().get('content', [])
            table = Table(title=f"ÉVÉNEMENTS : {q.upper()}", show_lines=True)
            table.add_column("DATE"); table.add_column("TITRE"); table.add_column("VILLE")
            for ev in events[:10]: table.add_row(ev.get('dateEvenement', '').split('T')[0], ev.get('titre'), ev.get('ville'))
            console.print(table)
        questionary.press_any_key_to_continue().ask()

if __name__ == "__main__":
    try: SwarmStation().main_menu()
    except KeyboardInterrupt: pass
