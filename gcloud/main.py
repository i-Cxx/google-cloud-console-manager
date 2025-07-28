import os
import sys

import subprocess
import time
import datetime
import json
import asyncio
import _queue
import shlex
import re, glob

import logging

import pickle






import os, pickle
import pathlib
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Log, ListView, ListItem, Label, Button, TabbedContent, Tabs, TabPane, Input, ProgressBar
from textual.containers import Container, Horizontal, Vertical, VerticalScroll

from textual.reactive import reactive
from textual import events



from api import gcloud_api



logging.basicConfig(level=logging.INFO)





os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


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


def login():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔁 Token abgelaufen. Versuche zu aktualisieren ...")
            creds.refresh(Request())
        else:
            print("🌐 Öffne Browser für Login ...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    print("✅ Login erfolgreich!")
    print("🔑 Zugriffstoken:", creds.token)
    
    
    

################# TEXTUAL BEREICH ########################################################

class OutputConsole(Static):
    def append(self, message: str):
        self.update(self.renderable + "\n" + message if self.renderable else message)


class HomeTab(TabPane):
    def compose(self) -> ComposeResult:
        yield Static("Home Tab Content", id="home_label", classes="header")
     

class SettingsTab(TabPane):
    def compose(self) -> ComposeResult:
        yield Static("Settings Tab Content", id="settings_label", classes="header")
        
       


class ProjectsTab(TabPane):
    CSS_PATH = "tui/projects.tcss"
    
    
    def compose(self) -> ComposeResult:
        
        yield VerticalScroll(Static("Drücke [b]L[/b], um GCP-Projekte zu laden.\n", id="output"), id="output_container")
        yield Vertical(Button("📋 GCP-Projekte laden", id="load_projects"))

        
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


class ConsoleTab(TabPane):
    def compose(self) -> ComposeResult:
        yield Static("Console Tab Content", id="console_label", classes="header")
        
        yield VerticalScroll(
            Static("Drücke [b]C[/b], um die GCloud Console zu autorisieren!\n", id="instruction_text"), 
            id="console_output_container"
        )
        
        yield Vertical(
            Button("Authenticate", id="load_projects")
        )
        
        yield Container(
            Static("Console:", id="console_label", classes="console"),
            Log(id="console_output", classes="output"),
            Input(placeholder="Type in any command! ... .. .", id="command_input", classes="input_field"),
            Button("Send", id="send_button", classes="button"),
            ProgressBar(show_eta=False, show_percentage=True, id="console_progressbar", classes="progressbar"),
            id="console_tab_container"
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load_projects":
            await self.authenticate_and_list_projects()
        elif event.button.id == "send_button":
            await self.execute_command()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "command_input":
            await self.execute_command()

    async def authenticate_and_list_projects(self):
        log = self.query_one("#console_output", Log)
        progress = self.query_one(ProgressBar)
        log.write("[cyan]🔐 Authentifiziere...")
        progress.update(total=100, progress=10)
        try:
            projects = gcloud_api.list_projects()
            log.write(f"[green]✅ {len(projects)} Projekte gefunden:")
            for proj in projects:
                name = proj.get('name', '<Kein Name>')
                project_id = proj.get('projectId', '<Keine ID>')
                log.write(f"- {name} ({project_id})")
            progress.update(total=100, progress=100)
        except Exception as e:
            log.write(f"[red]❌ Fehler: {e}")
            progress.update(total=100, progress=0)

    async def execute_command(self):
        command_input = self.query_one("#command_input", Input)
        command = command_input.value.strip()
        if not command:
            return

        log = self.query_one("#console_output", Log)
        log.write(f"[yellow]$ {command}")

        try:
            # Beispiel für einfache Kommandoauswertung
            if command.lower() == "list projects":
                projects = gcloud_api.list_projects()
                log.write(f"[green]✅ {len(projects)} Projekte gefunden:")
                for proj in projects:
                    name = proj.get('name', '<Kein Name>')
                    project_id = proj.get('projectId', '<Keine ID>')
                    log.write(f"- {name} ({project_id})")
            else:
                # Hier kannst du weitere Befehle interpretieren oder API-Aufrufe machen
                log.write(f"[cyan]Befehl nicht erkannt oder noch nicht implementiert: {command}")
        except Exception as e:
            log.write(f"[red]❌ Fehler bei Ausführung: {e}")

        # Eingabefeld leeren
        command_input.value = ""


class VMTab(TabPane):
    def compose(self) -> ComposeResult:
        yield Static("VM's Tab Content", id="vm_label",  classes="header")
        
        yield VerticalScroll(
            Static("VM-Instanzen", id="vm_output"), 
            id="vm_output_container"
        )
        
        yield Vertical(
            Button("Zeige VM's", id="load_vms")
        )




class LogTab(TabPane):
    def compose(self) -> ComposeResult:
        yield Static("Logs Tab Content", id="logs_label", classes="header")
        
        
        yield Label("Output - Logs: ", id="logs_header", classes="header_label")
        
        yield VerticalScroll(
            Static("Drücke [b]O[/b], um Logs zu laden.\n", id="log_output"), 
        
            id="log_output_container"
        )
        
        yield Vertical(
            Button("Logs Laden", id="load_projects")
        
        
        )







class GCloudConsoleApp(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [("q", "quit", "Quit")]
    TITLE = "Google Cloud Console - Manager"

    def compose(self) -> ComposeResult:
        yield Header()
        
        with TabbedContent(id="app-tabs"):
            yield HomeTab("Home")      
            yield SettingsTab("Settings")
            yield ProjectsTab("Projects")
            yield ConsoleTab("Console") 
            yield VMTab("VM-Instanzen")
            yield LogTab("Logs")
        
        yield Footer()




if __name__ == "__main__":
    GCloudConsoleApp().run()
