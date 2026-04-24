# 📘 Documentation Technique - Swarm Explorer v13.0

## 1. Architecture Système
L'application repose sur une architecture **modulaire découplée**, facilitant la maintenance de chaque connecteur API.

### 📁 Structure des Dossiers
- `src/auth/` : Singleton de gestion du flux OAuth 2.0 avec cache TTL (25 min).
- `src/clients/` : Connecteurs REST pour les API (Offres, Événements, Territoire, ROME).
- `src/core/` : Cœur algorithmique (Matching, Adaptation, Résilience, Géo).
- `profiles/` : Persistance des profils utilisateurs en format JSON.

## 2. Flux d'Authentification (OAuth 2.0)
Le système utilise le flux **Client Credentials** avec le royaume `/partenaire`.
- **Mécanisme de Cache** : Les jetons sont stockés dans `.ft_token_cache` pour éviter la saturation des quotas.
- **Scope Contractuel** : Les portées sont dynamiquement assemblées (ex: `application_{ID} api_offresdemploiv2 o2dsoffre`).

## 3. Algorithmes de Performance
### 🎯 Smart Matching (Optimisé v13.0)
L'algorithme de matching a été optimisé pour une complexité **O(N)** :
1. **Vectorisation** : Conversion du profil et de l'offre en vecteurs de mots-clés uniques (Sets).
2. **Similitude de Jaccard** : Calcul de l'intersection des vecteurs pour mesurer la proximité sémantique.
3. **Pondération Métier** : Un bonus de 40% est appliqué si le métier cible est détecté dans l'intitulé de l'offre via une recherche d'expression régulière.

### 🛡️ Moteur de Résilience
Le décorateur `@rate_limit_and_backoff` gère les limitations asymétriques :
- **Backoff Exponentiel** : Attente de (2^n + jitter) secondes en cas d'erreur 429.
- **Isolation des pannes** : Un échec sur une API (ex: Territoire) n'interrompt pas le flux principal.

## 4. Analyse de Données
### 📄 Parser de CV PDF
- Utilise la bibliothèque `pypdf` pour l'extraction de couches textuelles.
- **Extraction Sémantique** : Recherche de mots-clés par familles (Informatique, Restauration, Soft-skills).

### 🌍 Géo-Précision
- Conversion des noms de villes en codes INSEE via un dictionnaire de mapping optimisé.
- Paramètre `distance` forcé à 5km minimum pour contourner les bugs de l'API France Travail v2.

## 5. Maintenance et Évolutivité
Pour ajouter une nouvelle ville, modifier `src/core/geo.py`. Pour un nouveau service, créer une classe dans `src/clients/` héritant de la logique de résilience.
