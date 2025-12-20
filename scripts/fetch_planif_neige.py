#!/usr/bin/env python3
"""
Fetch data from Planif-Neige API and save to JSON file.
"""

import os
import json
from datetime import datetime, timedelta
from zeep import Client
from zeep.transports import Transport
from zeep.plugins import Plugin
from requests import Session

# Configuration
API_TOKEN = os.getenv('PLANIF_NEIGE_TOKEN')
WSDL_URL = "https://servicesenligne2.ville.montreal.qc.ca/api/infoneige/InfoneigeWebService?wsdl"
OUTPUT_FILE = "data/planif-neige.json"
METADATA_FILE = "data/planif-neige-metadata.json"

# API Error Codes
API_ERROR_OK = 0
API_ERROR_ACCESS_DENIED = 1
API_ERROR_INVALID_ACCESS = 2
API_ERROR_INVALID_DATE = 3
API_ERROR_RATE_LIMIT = 5
API_ERROR_NO_DATA = 8


class UserAgentPlugin(Plugin):
    """Zeep plugin to ensure User-Agent header is sent on SOAP requests."""

    def __init__(self, user_agent: str):
        """Initialize plugin with User-Agent string."""
        self.user_agent = user_agent

    def egress(self, envelope, http_headers, operation, binding_options):
        """Add User-Agent to outgoing HTTP headers."""
        http_headers["User-Agent"] = self.user_agent
        return envelope, http_headers


class CustomTransport(Transport):
    """Custom Zeep Transport that forces User-Agent on all HTTP requests."""

    def __init__(self, user_agent: str, **kwargs):
        """Initialize with User-Agent header."""
        super().__init__(**kwargs)
        self.user_agent = user_agent

    def _load_remote_data(self, url):
        """Override to add User-Agent header to GET requests."""
        if self.session:
            self.session.headers['User-Agent'] = self.user_agent
        return super()._load_remote_data(url)


def fetch_planif_neige_data():
    """Fetch data from Planif-Neige API."""

    print("🔄 Fetching data from Planif-Neige API...")

    # Initialize SOAP client
    session = Session()
    session.verify = True

    # Add browser User-Agent to avoid bot detection/blocking by Cloudflare
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    session.headers.update({'User-Agent': user_agent})

    # Use custom transport that forces User-Agent on all HTTP requests
    transport = CustomTransport(user_agent=user_agent, session=session, timeout=30)

    # Create plugin to ensure User-Agent is sent on SOAP requests
    user_agent_plugin = UserAgentPlugin(user_agent)

    client = Client(
        wsdl=WSDL_URL,
        transport=transport,
        plugins=[user_agent_plugin]
    )

    # Get data from last 7 days to ensure we have everything
    from_date = datetime.now() - timedelta(days=7)
    from_date_str = from_date.strftime("%Y-%m-%dT%H:%M:%S")

    try:
        # Call the API
        response = client.service.GetPlanificationsForDate(
            getPlanificationsForDate={
                'fromDate': from_date_str,
                'tokenString': API_TOKEN,
            }
        )

        # Parse response
        data = parse_response(response)

        # Save data to JSON
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Save metadata
        metadata = {
            "last_update": datetime.now().isoformat(),
            "from_date": from_date_str,
            "record_count": len(data.get('planifications', [])),
            "status": "success"
        }

        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✅ Successfully fetched {metadata['record_count']} records")
        return True

    except Exception as e:
        print(f"❌ Error fetching data: {e}")

        # Save error metadata
        metadata = {
            "last_update": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }

        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return False


def parse_response(response):
    """Parse SOAP response and convert to JSON-friendly format."""

    # Extract return code
    return_code = getattr(response, "responseStatus", None)

    if return_code is None:
        raise Exception("Missing return code in response")

    print(f"API returned code: {return_code}")

    # Handle error codes
    if return_code == API_ERROR_ACCESS_DENIED:
        raise Exception("Access denied - invalid token")

    if return_code == API_ERROR_INVALID_ACCESS:
        raise Exception("Invalid access - check parameters")

    if return_code == API_ERROR_RATE_LIMIT:
        raise Exception("Rate limit exceeded - wait 5 minutes")

    if return_code == API_ERROR_INVALID_DATE:
        raise Exception("Invalid date format")

    # Code 8 (no data) is not an error, just means no updates
    if return_code == API_ERROR_NO_DATA:
        print("No data for requested range")
        return {
            "planifications": [],
            "generated_at": datetime.now().isoformat()
        }

    if return_code != API_ERROR_OK:
        raise Exception(f"Unknown error code: {return_code}")

    # Extract planifications wrapper object
    planif_wrapper = getattr(response, "planifications", None)

    planifications = []
    if planif_wrapper:
        # The actual planifications are in the 'planification' attribute (without 's')
        planif_list = getattr(planif_wrapper, "planification", None)

        if planif_list:
            # Handle both single item and list
            if not isinstance(planif_list, list):
                planif_list = [planif_list]

            for planif in planif_list:
                planifications.append(parse_planification(planif))

    print(f"Parsed {len(planifications)} planifications")

    return {
        "planifications": planifications,
        "generated_at": datetime.now().isoformat()
    }


def parse_planification(planif):
    """Parse a single planification object."""

    return {
        "mun_id": getattr(planif, "munid", None),
        "cote_rue_id": getattr(planif, "coteRueId", None),
        "etat_deneig": getattr(planif, "etatDeneig", None),
        "date_deb_planif": format_datetime(
            getattr(planif, "dateDebutPlanif", None)
        ),
        "date_fin_planif": format_datetime(
            getattr(planif, "dateFinPlanif", None)
        ),
        "date_deb_replanif": format_datetime(
            getattr(planif, "dateDebutReplanif", None)
        ),
        "date_fin_replanif": format_datetime(
            getattr(planif, "dateFinReplanif", None)
        ),
        "date_maj": format_datetime(
            getattr(planif, "dateMaj", None)
        ),
    }


def format_datetime(dt):
    """Format datetime to ISO 8601 string."""

    if not dt:
        return None

    # If already a datetime object, format it
    if isinstance(dt, datetime):
        return dt.isoformat()

    # If it's a string, return as-is
    return str(dt)


if __name__ == "__main__":
    if not API_TOKEN:
        print("❌ Error: PLANIF_NEIGE_TOKEN environment variable not set")
        exit(1)

    success = fetch_planif_neige_data()
    exit(0 if success else 1)
