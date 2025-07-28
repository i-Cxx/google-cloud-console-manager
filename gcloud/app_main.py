import os
import sys

import subprocess
import time

import datetime
import asyncio
import _queue
import shlex
import re, glob



import pickle





from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Label, Button, TabbedContent, Tabs, TabPane #, Progressbar
from textual.containers import Vertical, VerticalScroll




SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_DIR = os.path.join(BASE_DIR, "keys")
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






class GCloudConsoleApp(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(Static("Drücke [b]L[/b], um GCP-Projekte zu laden.\n", id="output"), id="output_container")
        yield Vertical(Button("📋 GCP-Projekte laden", id="load_projects"))
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load_projects":
            output_widget = self.query_one("#output", Static)
            output_widget.update("🔄 Lade GCP-Projekte ...")
            try:
                projects = list_projects()  # hier direkt die Funktion nutzen
                output = "\n".join(
                    f"🔹 {p.get('projectId')} ({p.get('name', 'Kein Name')}) - {p.get('lifecycleState', 'Unbekannt')}"
                    for p in projects
                )
                output_widget.update(f"📋 Gefundene Projekte:\n\n{output}")
            except Exception as e:
                output_widget.update(f"❌ Fehler: {e}")


if __name__ == "__main__":
    GCloudConsoleApp().run()
