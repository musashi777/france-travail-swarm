import sys
import os
import questionary
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
from src.core.cv_processor import extract_text_from_pdf, analyze_cv_content
from src.core.history import record_application, load_history

console = Console()

class SwarmTUI:
    def __init__(self):
        with console.status("[bold blue]Lancement de l'intelligence Swarm...", spinner="dots"):
            self.auth = FranceTravailAuth()
            self.events_api = EvenementsClient(self.auth)
            self.jobs_api = OffresClient(self.auth)
            self.territory_api = TerritoireClient(self.auth)
            self.active_profile = None
            self.active_profile_name = "Aucun"

    def welcome_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')
        rprint(Panel.fit(
            f"[bold cyan]🚀 SWARM EMPLOI v13.0 - ÉLITE[/bold cyan]\n"
            f"[bold yellow]Profil Actif : {self.active_profile_name}[/bold yellow]",
            border_style="bright_magenta"
        ))

    def main_menu(self):
        while True:
            self.welcome_screen()
            choice = questionary.select(
                "Tableau de Bord :",
                choices=[
                    "👤 Gestion des Profils",
                    "💼 Chercher des Offres",
                    "📜 Historique des Candidatures",
                    "📅 Explorer les Événements",
                    "🚪 Quitter"
                ]
            ).ask()

            if "Profils" in choice: self.ui_profile_manager()
            elif "Offres" in choice: self.ui_offres()
            elif "Historique" in choice: self.ui_history()
            elif "Événements" in choice: self.ui_evenements()
            else: break

    def ui_history(self):
        self.welcome_screen()
        history = load_history()
        if not history:
            rprint("[yellow]Aucune candidature enregistrée pour le moment.[/yellow]")
        else:
            table = Table(title="📜 MES DERNIÈRES ACTIONS", show_lines=True)
            table.add_column("DATE", style="cyan")
            table.add_column("ENTREPRISE", style="green")
            table.add_column("POSTE", style="white bold")
            table.add_column("PROFIL", style="yellow")
            
            for h in history:
                table.add_row(h['date'], h['entreprise'], h['intitule'], h['profil_utilise'])
            console.print(table)
        questionary.press_any_key_to_continue().ask()

    def ui_profile_manager(self):
        while True:
            self.welcome_screen()
            profiles = list_profiles()
            choice = questionary.select(
                "Gestion des profils :",
                choices=["✅ Sélectionner", "➕ Créer", "📝 Modifier", "🗑️ Supprimer", "❌ Désactiver", "⬅️ Retour"]
            ).ask()

            if "Sélectionner" in choice:
                if not profiles: continue
                name = questionary.select("Choisir :", choices=profiles).ask()
                self.active_profile = load_profile(name)
                self.active_profile_name = name
                break
            elif "Créer" in choice:
                self.ui_create_profile()
                break
            elif "Modifier" in choice:
                if self.active_profile: self.ui_edit_current_profile()
            elif "Supprimer" in choice:
                if not profiles: continue
                name = questionary.select("Supprimer :", choices=profiles).ask()
                if questionary.confirm("Confirmer ?").ask():
                    if delete_profile(name):
                        if self.active_profile_name == name:
                            self.active_profile, self.active_profile_name = None, "Aucun"
            elif "Désactiver" in choice:
                self.active_profile, self.active_profile_name = None, "Aucun"
                break
            else: break

    def ui_create_profile(self):
        method = questionary.select("Méthode :", choices=["📄 Importer CV", "⌨️ Saisie Manuelle"]).ask()
        name = questionary.text("Nom du métier (ex: Cuisine) :").ask()
        data = {"nom": "Candidat", "competences": [], "experiences": name}
        if "CV" in method:
            path = questionary.text("Chemin PDF :").ask()
            if os.path.exists(path):
                text = extract_text_from_pdf(path)
                cv_data = analyze_cv_content(text)
                if cv_data: data.update(cv_data)
        save_profile(name, data)
        self.active_profile, self.active_profile_name = data, name

    def ui_edit_current_profile(self):
        self.active_profile['nom'] = questionary.text("Nom :", default=self.active_profile.get('nom', '')).ask()
        comps = questionary.text("Compétences (virgule) :", default=",".join(self.active_profile.get('competences', []))).ask()
        self.active_profile['competences'] = [c.strip() for c in comps.split(',') if c.strip()]
        self.active_profile['experiences'] = questionary.text("Métier :", default=self.active_profile.get('experiences', '')).ask()
        save_profile(self.active_profile_name, self.active_profile)

    def ui_offres(self):
        default_q = self.active_profile.get('experiences', '') if self.active_profile else "Polyvalent"
        query = questionary.text("Métier recherché :", default=default_q).ask()
        ville = questionary.text("Ville :", default="Marseille").ask()
        insee = get_insee_code(ville)
        with console.status(f"[bold blue]Recherche à {ville}..."):
            res = self.jobs_api.search(mots_cles=query, commune=insee, distance=5)
        if res and res.status_code in [200, 206]:
            self.browse_offres(res.json().get('resultats', []))
        else:
            rprint("[yellow]Aucune offre.[/yellow]")
            questionary.press_any_key_to_continue().ask()

    def browse_offres(self, offres):
        while True:
            self.welcome_screen()
            choices = []
            for i, o in enumerate(offres):
                score_str = f"[{calculate_match_score(self.active_profile, o)}%] " if self.active_profile else ""
                choices.append(questionary.Choice(title=f"{score_str}{o.get('intitule')}", value=i))
            choices.append(questionary.Choice(title="[Retour]", value="back"))
            idx = questionary.select("Résultats :", choices=choices).ask()
            if idx == "back": break
            self.display_job_detail(offres[idx])

    def display_job_detail(self, o):
        self.welcome_screen()
        score = calculate_match_score(self.active_profile, o) if self.active_profile else None
        detail = Text()
        if score is not None:
            detail.append(f"\n🎯 MATCHING : {score}%\n", style="bold magenta")
        detail.append(f"🏢 Entreprise : {o.get('entreprise', {}).get('nom')}\n", style="bold green")
        detail.append(f"📄 Contrat    : {o.get('typeContratLibelle')}\n")
        detail.append(f"\n📝 DESCRIPTION :\n{o.get('description', 'N/A')[:500]}...\n")
        rprint(Panel(detail, title=f"[bold white]{o.get('intitule')}[/bold white]", border_style="cyan"))
        
        actions = ["🔗 Voir en ligne", "⬅️ Retour"]
        if self.active_profile:
            actions.insert(0, "🛠️ Adapter mon CV")
            actions.insert(0, "📝 Générer Lettre")
        
        act = questionary.select("Action :", choices=actions).ask()
        if "Lettre" in act:
            record_application(o, self.active_profile_name, "Lettre générée")
            rprint(Panel(generate_cover_letter(self.active_profile, o), title="LETTRE", border_style="green"))
            questionary.press_any_key_to_continue().ask()
        elif "Adapter" in act:
            record_application(o, self.active_profile_name, "CV Adapté")
            advice = generate_cv_adaptation(self.active_profile, o)
            rprint(Panel(advice, title="🛠️ CONSEILS D'ADAPTATION CV", border_style="bright_cyan"))
            questionary.press_any_key_to_continue().ask()

    def ui_evenements(self):
        query = questionary.text("Métier :", default="Restauration").ask()
        ville = questionary.text("Ville :", default="Marseille").ask()
        insee = get_insee_code(ville)
        with console.status("[bold cyan]Recherche d'événements..."):
            res = self.events_api.search_advanced(departement=insee[:2], mots_cles=query)
        if res and res.status_code == 200:
            events = res.json().get('content', [])
            self.display_events_table(events, query)
        questionary.press_any_key_to_continue().ask()

    def display_events_table(self, events, query):
        table = Table(title=f"📅 ÉVÉNEMENTS : {query.upper()}", show_lines=True)
        table.add_column("DATE", style="cyan"); table.add_column("TITRE", style="white bold"); table.add_column("VILLE", style="magenta")
        for ev in events[:10]:
            table.add_row(ev.get('dateEvenement', '').split('T')[0], ev.get('titre'), ev.get('ville'))
        console.print(table)

if __name__ == "__main__":
    try: SwarmTUI().main_menu()
    except KeyboardInterrupt: pass
