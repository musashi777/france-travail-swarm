# 🚀 France Travail Swarm Explorer v13.0

Assistant de recherche d'emploi intelligent utilisant les API officielles de France Travail. Cet outil permet de centraliser la recherche d'offres, de Job Datings et propose un coaching personnalisé.

## ✨ Fonctionnalités
- **🔍 Multi-Search** : Recherche simultanée d'offres et d'événements.
- **🎯 Smart Matching** : Calcul du taux d'adéquation entre votre CV et l'offre.
- **📄 CV PDF Parser** : Extraction automatique de compétences depuis un PDF.
- **🛠️ CV Adapter** : Conseils concrets pour adapter votre CV à une annonce.
- **📝 Cover Letter AI** : Génération de brouillons de lettres de motivation.
- **📜 Historique** : Suivi de vos candidatures et actions.

## 🛠️ Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-compte/votre-repo.git
   cd votre-repo
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurer vos accès :
   Créez un fichier `.env` à la racine avec vos identifiants France Travail :
   ```env
   FT_CLIENT_ID=votre_id
   FT_CLIENT_SECRET=votre_secret
   ```

## 🚀 Utilisation
Lancez l'interface interactive :
```bash
python main.py
```

## 🛡️ Sécurité
Le fichier `.env` est exclu du dépôt via `.gitignore`. Ne committez jamais vos clés API.
