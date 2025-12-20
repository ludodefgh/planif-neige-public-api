# Planif-Neige Public API

API publique non-officielle pour accéder aux données de déneigement de Montréal (système Planif-Neige).

## 🎯 Objectif

Fournir un accès simple et gratuit aux données de déneigement de Montréal sans que chaque utilisateur ait besoin d'obtenir un token API auprès de la Ville.

## 📡 Endpoints

### Données de déneigement (mis à jour toutes les 10 minutes)

```
https://raw.githubusercontent.com/ludodefgh/planif-neige-public-api/main/data/planif-neige.json
```

**Format** :
```json
{
  "planifications": [
    {
      "mun_id": 1,
      "cote_rue_id": 12345,
      "etat_deneig": 2,
      "date_deb_planif": "2024-12-20T07:00:00",
      "date_fin_planif": "2024-12-20T19:00:00",
      "date_deb_replanif": null,
      "date_fin_replanif": null,
      "date_maj": "2024-12-19T15:00:00"
    }
  ],
  "generated_at": "2024-12-20T12:34:56"
}
```

### Mapping des rues (mis à jour hebdomadairement)

```
https://raw.githubusercontent.com/ludodefgh/planif-neige-public-api/main/data/geobase-map.json
```

**Format** :
```json
{
  "12345": {
    "nom_voie": "Saint-Denis",
    "type_voie": "rue",
    "debut_adresse": 100,
    "fin_adresse": 199,
    "cote": "Gauche",
    "nom_ville": "MTL"
  }
}
```

### Métadonnées

```
https://raw.githubusercontent.com/ludodefgh/planif-neige-public-api/main/data/planif-neige-metadata.json
```

**Format** :
```json
{
  "last_update": "2024-12-20T12:34:56",
  "from_date": "2024-12-13T12:34:56",
  "record_count": 1234,
  "status": "success"
}
```

## 🔄 Fréquence de mise à jour

- **Données de déneigement** : Toutes les 10 minutes (via GitHub Actions)
- **Mapping géobase** : Hebdomadaire (dimanche 3h AM)

## 📊 États de déneigement

| Code | État | Description |
|------|------|-------------|
| 0 | Enneigé | Pas encore déneigé |
| 1 | Déneigé | Chargement complété |
| 2 | Planifié | Chargement planifié |
| 3 | Replanifié | Reporté à une nouvelle date |
| 4 | Sera replanifié | Reporté sans date |
| 5 | En cours | Chargement en cours |
| 10 | Dégagé | Entre deux chargements |

## 🏗️ Utilisation

### Intégration Home Assistant

Cette API est utilisée par l'intégration [montreal-snow-removal](https://github.com/ludodefgh/montreal-snow-removal).

### Utilisation directe

```python
import requests

# Récupérer les données
response = requests.get("https://raw.githubusercontent.com/ludodefgh/planif-neige-public-api/main/data/planif-neige.json")
data = response.json()

# Récupérer le mapping
response = requests.get("https://raw.githubusercontent.com/ludodefgh/planif-neige-public-api/main/data/geobase-map.json")
mapping = response.json()

# Trouver l'état d'un côté de rue
for planif in data['planifications']:
    cote_rue_id = str(planif['cote_rue_id'])
    street_info = mapping.get(cote_rue_id, {})
    print(f"{street_info.get('nom_voie')} - État: {planif['etat_deneig']}")
```

## ⚖️ Licence et source des données

Les données proviennent du système Planif-Neige de la Ville de Montréal, disponibles sous licence de données ouvertes.

- **Source officielle** : [Données ouvertes Montréal](https://donnees.montreal.ca/dataset/deneigement)
- **API officielle** : Requiert un token (demande à donneesouvertes@montreal.ca)

**Avertissement** : La signalisation en vigueur dans les rues prévaut toujours sur les données de l'API.

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📧 Contact

Ludodefgh - [@ludodefgh](https://github.com/ludodefgh)

---

**Note** : Ce projet n'est pas affilié à la Ville de Montréal. C'est un projet communautaire indépendant.
