# Configuration du projet Planif-Neige Public API

Ce document décrit les étapes pour configurer le projet après sa création sur GitHub.

## ✅ Étapes déjà complétées

- [x] Création de la structure du projet
- [x] Création de tous les fichiers nécessaires
- [x] Initialisation du dépôt Git
- [x] Push du code vers GitHub

## 🔧 Étapes de configuration à effectuer

### 1. Ajouter le secret GitHub Actions

Le workflow GitHub Actions a besoin du token API Planif-Neige pour fonctionner.

**Étapes** :

1. Aller sur https://github.com/ludodefgh/planif-neige-public-api/settings/secrets/actions
2. Cliquer sur "New repository secret"
3. Nom : `PLANIF_NEIGE_TOKEN`
4. Valeur : Votre token API de la Ville de Montréal
5. Cliquer "Add secret"

### 2. Configurer les permissions GitHub Actions

GitHub Actions a besoin de permissions pour commit et push les fichiers JSON.

**Étapes** :

1. Aller sur https://github.com/ludodefgh/planif-neige-public-api/settings/actions
2. Dans la section "Workflow permissions", sélectionner :
   - ✅ **Read and write permissions**
3. Cliquer "Save"

### 3. Tester le workflow manuellement

Avant de laisser le cron s'exécuter automatiquement, testez le workflow manuellement.

**Étapes** :

1. Aller sur https://github.com/ludodefgh/planif-neige-public-api/actions
2. Cliquer sur "Fetch Planif-Neige Data" dans la liste des workflows
3. Cliquer "Run workflow" → "Run workflow"
4. Attendre la fin de l'exécution (environ 1-2 minutes)
5. Vérifier que les fichiers JSON ont été créés dans le dossier `data/`

### 4. Vérifier l'accès public aux données

Une fois que les fichiers JSON sont créés, testez l'accès public :

```bash
# Tester l'accès aux métadonnées
curl https://raw.githubusercontent.com/ludodefgh/planif-neige-public-api/main/data/planif-neige-metadata.json

# Tester l'accès aux données complètes
curl https://raw.githubusercontent.com/ludodefgh/planif-neige-public-api/main/data/planif-neige.json

# Tester l'accès au mapping géobase (après avoir exécuté le workflow de géobase)
curl https://raw.githubusercontent.com/ludodefgh/planif-neige-public-api/main/data/geobase-map.json
```

### 5. Tester le workflow de géobase

Le workflow de géobase s'exécute hebdomadairement, mais vous pouvez le tester manuellement.

**Étapes** :

1. Aller sur https://github.com/ludodefgh/planif-neige-public-api/actions
2. Sélectionner le workflow "Fetch Planif-Neige Data"
3. Cliquer "Run workflow"
4. Attendre la fin de l'exécution
5. Vérifier que `data/geobase-map.json` a été créé

### 6. (Optionnel) Ajouter une page GitHub Pages

Vous pouvez créer une page de statut simple avec GitHub Pages.

**Étapes** :

1. Aller sur https://github.com/ludodefgh/planif-neige-public-api/settings/pages
2. Source : Deploy from a branch
3. Branch : `main`, Folder : `/ (root)`
4. Cliquer "Save"

## 🔍 Vérification du bon fonctionnement

### Vérifier les workflows

- Les workflows s'exécutent toutes les 10 minutes automatiquement
- Vérifier dans l'onglet Actions qu'il n'y a pas d'erreurs
- Les commits automatiques devraient apparaître avec le message "Update Planif-Neige data - [date]"

### Vérifier les données

Les fichiers suivants devraient exister dans le dossier `data/` :

- `planif-neige.json` - Données de déneigement
- `planif-neige-metadata.json` - Métadonnées (dernière mise à jour, nombre de records)
- `geobase-map.json` - Mapping des COTE_RUE_ID vers les noms de rues

## 📧 Support

Si vous rencontrez des problèmes :

1. Vérifier les logs dans l'onglet Actions
2. Vérifier que le token API est valide
3. Vérifier les permissions GitHub Actions
4. Ouvrir une issue sur le dépôt si le problème persiste

## 🚀 Prochaines étapes

Une fois que l'API publique fonctionne :

1. Modifier l'intégration Home Assistant `montreal-snow-removal` pour utiliser cette API publique
2. Supprimer le besoin de token API dans le custom component
3. Simplifier le processus de configuration pour les utilisateurs
4. Publier la mise à jour sur HACS

---

**Note** : N'oubliez pas de contacter la Ville de Montréal (donneesouvertes@montreal.ca) pour confirmer que la redistribution des données est acceptable.
