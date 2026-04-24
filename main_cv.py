import sys
import os
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth.manager import FranceTravailAuth
from src.clients.offres import OffresClient
from src.core.geo import get_insee_code
from src.core.profile import load_profile, list_profiles
from src.core.matching import calculate_match_score
from src.core.cv_generator import create_full_cv_pdf, get_cv_content_structure
from src.core.history import record_application

console = Console()

class SwarmCV:
    def __init__(self):
        self.auth = FranceTravailAuth()
        self.jobs_api = OffresClient(self.auth)
        self.active_profile = None
        self.active_profile_name = "Aucun"

    def main_menu(self):
        while True:
            os.system('clear' if os.name != 'nt' else 'cls')
            rprint(Panel.fit("[bold cyan]🚀 GÉNÉRATEUR DE CV v15.5[/bold cyan]\n[italic]Mode Aperçu Avant Export[/italic]", border_style="blue"))
            
            choice = questionary.select(
                "Menu :",
                choices=["👤 Choisir mon Profil", "💼 Chercher et Prévisualiser", "🚪 Quitter"]
            ).ask()

            if "Profil" in choice:
                profiles = list_profiles()
                if profiles:
                    name = questionary.select("Profil :", choices=profiles).ask()
                    self.active_profile, self.active_profile_name = load_profile(name), name
                else:
                    rprint("[yellow]Créez un profil dans l'appli principale.[/yellow]")
                    questionary.press_any_key_to_continue().ask()
            elif "Chercher" in choice:
                self.ui_offres()
            else: break

    def ui_offres(self):
        query = questionary.text("Métier :", default=self.active_profile.get('experiences', '') if self.active_profile else "Polyvalent").ask()
        ville = questionary.text("Ville :").ask()
        insee = get_insee_code(ville)
        
        with console.status("[bold blue]Recherche en cours..."):
            res = self.jobs_api.search(mots_cles=query, commune=insee, distance=10)
        
        if res and res.status_code in [200, 206]:
            offres = res.json().get('resultats', [])
            self.browse_offres(offres)
        else:
            rprint("[red]Aucune offre trouvée.[/red]")
            questionary.press_any_key_to_continue().ask()

    def browse_offres(self, offres):
        choices = [questionary.Choice(title=f"[{calculate_match_score(self.active_profile, o)}%] {o.get('intitule')}", value=i) for i, o in enumerate(offres)]
        choices.append(questionary.Choice(title="[Retour]", value="back"))
        
        idx = questionary.select("Offre à adapter :", choices=choices).ask()
        if idx != "back": self.preview_and_generate(offres[idx])

    def preview_and_generate(self, o):
        """Affiche un aperçu complet du CV avant de proposer l'exportation."""
        if not self.active_profile:
            rprint("[red]Erreur : Aucun profil sélectionné.[/red]")
            questionary.press_any_key_to_continue().ask()
            return

        struct = get_cv_content_structure(self.active_profile, o)
        
        os.system('clear')
        preview = Text()
        preview.append(f"\n📄 APERÇU DU CV POUR : {o.get('entreprise', {}).get('nom')}\n", style="bold underline cyan")
        preview.append(f"\nTITRE : {struct['poste']}\n", style="bold white")
        preview.append(f"\n📌 ACCROCHE GÉNÉRÉE :\n", style="bold yellow")
        preview.append(f"{struct['accroche']}\n")
        preview.append(f"\n🛠️ COMPÉTENCES MISES EN AVANT :\n", style="bold green")
        for s in struct['competences']:
            preview.append(f"  {s}\n")
        preview.append(f"\n[italic](Légende : [OK] = Dans votre CV, [+] = À rajouter)[/italic]\n")

        rprint(Panel(preview, title="👁️ MODE PRÉVISUALISATION", border_style="bright_blue"))
        
        action = questionary.select(
            "Validation :",
            choices=["💾 Exporter en PDF", "📝 Modifier mon profil d'abord", "⬅️ Retour à la liste"]
        ).ask()

        if "PDF" in action:
            filename = f"CV_{o.get('id')}.pdf"
            create_full_cv_pdf(self.active_profile, o, filename)
            rprint(f"[bold green]✅ CV PDF généré : {filename}[/bold green]")
            record_application(o, self.active_profile_name, "CV PDF Exporté")
            questionary.press_any_key_to_continue().ask()
        elif "Modifier" in action:
            rprint("[yellow]Utilisez le menu principal pour modifier vos compétences.[/yellow]")
            questionary.press_any_key_to_continue().ask()

if __name__ == "__main__":
    try: SwarmCV().main_menu()
    except KeyboardInterrupt: pass
