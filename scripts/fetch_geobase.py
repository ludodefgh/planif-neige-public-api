#!/usr/bin/env python3
"""
Fetch Geobase data from Montreal Open Data and create COTE_RUE_ID mapping.
"""

import json
import requests

# Configuration
GEOBASE_URL = "https://donnees.montreal.ca/dataset/88493b16-220f-4709-b57b-1ea57c5ba405/resource/16f7fa0a-9ce6-4b29-a7fc-00842c593927/download/gbdouble.json"
OUTPUT_FILE = "data/geobase-map.json"


def fetch_geobase_data():
    """Fetch Geobase data and create mapping."""

    print("🔄 Fetching Geobase data from Montreal Open Data...")

    try:
        # Download GeoJSON
        response = requests.get(GEOBASE_URL, timeout=60)
        response.raise_for_status()

        geobase_data = response.json()

        # Create mapping: COTE_RUE_ID -> street info
        mapping = {}

        for feature in geobase_data.get('features', []):
            props = feature.get('properties', {})

            cote_rue_id = props.get('COTE_RUE_ID')
            if not cote_rue_id:
                continue

            mapping[str(cote_rue_id)] = {
                "nom_voie": props.get('NOM_VOIE', ''),
                "type_voie": props.get('TYPE_F', ''),
                "debut_adresse": props.get('DEBUT_ADRESSE'),
                "fin_adresse": props.get('FIN_ADRESSE'),
                "cote": props.get('COTE', ''),
                "nom_ville": props.get('NOM_VILLE', '')
            }

        # Save mapping
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)

        print(f"✅ Successfully created mapping for {len(mapping)} street sides")
        return True

    except Exception as e:
        print(f"❌ Error fetching geobase: {e}")
        return False


if __name__ == "__main__":
    success = fetch_geobase_data()
    exit(0 if success else 1)
