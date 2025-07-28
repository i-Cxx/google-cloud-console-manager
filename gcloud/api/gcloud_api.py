import os, pickle
import pathlib
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CURRENT_FILE = Path(__file__).resolve()

# Projekt-Root (z. B. 2 Ebenen über api/gcloud_api.py)
PROJECT_ROOT = CURRENT_FILE.parents[1]

# Pfad zum "keys/"-Ordner im Projektroot
KEYS_DIR = PROJECT_ROOT / "keys"

# KEYS_DIR = os.path.join(BASE_DIR, "keys")
TOKEN_FILE = os.path.join(KEYS_DIR, "token.pickle")
CREDS_FILE = os.path.join(KEYS_DIR, "creds.json")

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    return creds

def list_projects():
    creds = get_credentials()
    service = build("cloudresourcemanager", "v1", credentials=creds)
    request = service.projects().list()
    projects = []
    while request:
        response = request.execute()
        projects.extend(response.get("projects", []))
        request = service.projects().list_next(previous_request=request, previous_response=response)
    return projects
