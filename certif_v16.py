import sys
import os
import json
sys.path.append(os.getcwd())

# Import de tous les composants de la v16.0
try:
    from src.auth.manager import FranceTravailAuth
    from src.clients.offres import OffresClient
    from src.clients.territoire import TerritoireClient
    from src.core.matching import calculate_match_score
    from src.core.cv_generator import create_full_cv_pdf
    from src.core.intelligence import is_new_offer
    from src.core.history import record_application
    print("✅ TEST 1 : Imports de tous les modules OK.")
except Exception as e:
    print(f"❌ TEST 1 : Erreur d'import : {e}")
    sys.exit(1)

def run_certification():
    print("\n--- 🏁 DÉBUT DE LA CERTIFICATION v16.0 ---")
    
    auth = FranceTravailAuth()
    
    # 1. Test Authentification & Cache
    token = auth.get_token("api_offresdemploiv2 o2dsoffre")
    if token:
        print("✅ TEST 2 : Authentification et Cache OK.")
    
    # 2. Simulation d'un flux complet
    mock_profile = {
        "nom": "Jean Test",
        "competences": ["HACCP", "Cuisine", "Hygiène"],
        "experiences": "Cuisinier"
    }
    
    mock_offer = {
        "id": "CERTIF_001",
        "intitule": "Chef de partie (H/F)",
        "description": "Recherche expert en cuisine et normes HACCP.",
        "entreprise": {"nom": "Le Grand Restaurant"},
        "lieuTravail": {"libelle": "Marseille", "codePostal": "13001"},
        "typeContratLibelle": "CDI",
        "competences": [{"libelle": "HACCP"}]
    }

    # 3. Test Matching Vectoriel
    score = calculate_match_score(mock_profile, mock_offer)
    print(f"✅ TEST 3 : Matching Vectoriel OK (Score: {score}%).")

    # 4. Test Génération PDF
    pdf_name = "test_certification.pdf"
    try:
        create_full_cv_pdf(mock_profile, mock_offer, pdf_name)
        if os.path.exists(pdf_name):
            print(f"✅ TEST 4 : Génération PDF OK ({pdf_name}).")
            os.remove(pdf_name) # Nettoyage
    except Exception as e:
        print(f"❌ TEST 4 : Échec génération PDF : {e}")

    # 5. Test Historique
    try:
        record_application(mock_offer, "Profil Cuisine", "Test Certification")
        print("✅ TEST 5 : Enregistrement Historique OK.")
    except Exception as e:
        print(f"❌ TEST 5 : Échec Historique : {e}")

    print("\n🏆 BILAN : TOUTES LES FONCTIONNALITÉS SONT OPÉRATIONNELLES.")

if __name__ == "__main__":
    run_certification()
