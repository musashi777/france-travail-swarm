import sys
import os
sys.path.append(os.getcwd())

from src.core.matching import calculate_match_score

def test_vector_matching():
    print("═══ 🧪 TEST DE PERFORMANCE : MATCHING VECTORIEL O(N) ═══\n")
    
    profile = {
        "competences": ["Python", "SQL", "Linux", "Maintenance"],
        "experiences": "Technicien Informatique"
    }

    offers = [
        {
            "intitule": "Technicien Support Informatique (H/F)",
            "description": "Maintenance de parcs informatiques sous Windows et Linux. Connaissances SQL.",
            "competences": [{"libelle": "Maintenance"}, {"libelle": "Linux"}]
        },
        {
            "intitule": "Serveur de restaurant",
            "description": "Service en salle et accueil client.",
            "competences": [{"libelle": "Service"}]
        }
    ]

    for i, o in enumerate(offers):
        score = calculate_match_score(profile, o)
        print(f"Offre {i+1} : {o['intitule']}")
        print(f"  🎯 Score : {score}%")
        if i == 0 and score > 40:
            print("  ✅ Match pertinent détecté.")
        if i == 1 and score < 10:
            print("  ✅ Faux positif correctement écarté.")

if __name__ == "__main__":
    test_vector_matching()
