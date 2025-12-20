#!/bin/bash
#
# Script de test local pour vérifier le bon fonctionnement des scripts
# avant de les déployer sur GitHub Actions
#

set -e

echo "🧪 Test local des scripts Planif-Neige Public API"
echo "=================================================="
echo ""

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✅ Python 3 trouvé: $(python3 --version)"
echo ""

# Créer un environnement virtuel temporaire
echo "📦 Création d'un environnement virtuel temporaire..."
python3 -m venv .venv_test
source .venv_test/bin/activate

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -q -r scripts/requirements.txt

echo "✅ Dépendances installées"
echo ""

# Test 1: Vérifier que le script fetch_geobase.py fonctionne
echo "🧪 Test 1: Téléchargement de la géobase..."
if python3 scripts/fetch_geobase.py; then
    echo "✅ Test 1 réussi: Géobase téléchargée"
    if [ -f "data/geobase-map.json" ]; then
        GEOBASE_SIZE=$(wc -c < data/geobase-map.json)
        echo "   Taille du fichier: $GEOBASE_SIZE bytes"
        # Compter le nombre d'entrées
        GEOBASE_COUNT=$(python3 -c "import json; data=json.load(open('data/geobase-map.json')); print(len(data))")
        echo "   Nombre d'entrées: $GEOBASE_COUNT"
    fi
else
    echo "❌ Test 1 échoué: Erreur lors du téléchargement de la géobase"
    deactivate
    rm -rf .venv_test
    exit 1
fi
echo ""

# Test 2: Vérifier que le token API est défini
echo "🧪 Test 2: Vérification du token API..."
if [ -z "$PLANIF_NEIGE_TOKEN" ]; then
    echo "⚠️  Test 2 ignoré: PLANIF_NEIGE_TOKEN non défini"
    echo "   Pour tester l'API, définir: export PLANIF_NEIGE_TOKEN=votre_token"
    echo ""
    echo "🎉 Tests terminés (1/2 exécutés)"
else
    echo "✅ Token API trouvé"
    echo ""

    # Test 3: Vérifier que le script fetch_planif_neige.py fonctionne
    echo "🧪 Test 3: Récupération des données Planif-Neige..."
    if python3 scripts/fetch_planif_neige.py; then
        echo "✅ Test 3 réussi: Données récupérées"
        if [ -f "data/planif-neige.json" ]; then
            PLANIF_SIZE=$(wc -c < data/planif-neige.json)
            echo "   Taille du fichier: $PLANIF_SIZE bytes"
        fi
        if [ -f "data/planif-neige-metadata.json" ]; then
            echo "   Métadonnées:"
            cat data/planif-neige-metadata.json | python3 -m json.tool
        fi
    else
        echo "❌ Test 3 échoué: Erreur lors de la récupération des données"
        deactivate
        rm -rf .venv_test
        exit 1
    fi
    echo ""
    echo "🎉 Tous les tests réussis!"
fi

# Nettoyage
echo ""
echo "🧹 Nettoyage..."
deactivate
rm -rf .venv_test

echo ""
echo "✅ Tests terminés avec succès!"
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Vérifier les fichiers JSON dans data/"
echo "   2. Pousser le code sur GitHub"
echo "   3. Configurer le secret PLANIF_NEIGE_TOKEN sur GitHub"
echo "   4. Activer les permissions GitHub Actions (Read and write)"
echo "   5. Tester le workflow manuellement"
