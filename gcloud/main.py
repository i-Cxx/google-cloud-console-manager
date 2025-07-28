import os
import sys

import subprocess
import time

import datetime
import asyncio
import _queue
import shlex
import re, glob

import logging

import pickle





from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Log, ListView, ListItem, Label, Button, TabbedContent, Tabs, TabPane, ProgressBar
from textual.containers import Container, Horizontal, Vertical, VerticalScroll









logging.basicConfig(level=logging.INFO)






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

# def get_credentials():
#     creds = None
#     if os.path.exists(TOKEN_FILE):
#         with open(TOKEN_FILE, "rb") as token:
#             creds = pickle.load(token)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
#             creds = flow.run_local_server(port=8080)
#         with open(TOKEN_FILE, "wb") as token:
#             pickle.dump(creds, token)
#     return creds


# def list_projects():
#     creds = get_credentials()
#     service = build("cloudresourcemanager", "v1", credentials=creds)
#     request = service.projects().list()
#     projects = []
#     while request:
#         response = request.execute()
#         projects.extend(response.get("projects", []))
#         request = service.projects().list_next(previous_request=request, previous_response=response)
#     return projects






################# TEXTUAL BEREICH ########################################################


class HomeTab(TabPane):
    def compose(self) -> ComposeResult:
        yield Static("Home Tab Content", id="home_label", classes="header")
     

class SettingsTab(TabPane):
    def compose(self) -> ComposeResult:
        yield Static("Settings Tab Content", id="settings_label", classes="header")
        
        yield VerticalScroll(
            Static(
                "Drücke [b]S[/b], um Settings zu laden.\n", id="setting_static"
            ), 
            
            
            id="home_output_container"
        )
        
        yield Vertical(
            Button("Load Settings", id="load_settings")
        
        )
        
        
class XXXTab(TabPane):
    def compose(self) -> ComposeResult:
        yield Static("Home Tab Content", id="home_label")
        yield VerticalScroll(Static("Drücke [b]L[/b], um GCP-Projekte zu laden.\n", id="home_output"), id="home_output_container")
        yield Vertical(Button("📦 GCP-Projekte laden", id="load_projects"))



class ProjectsTab(TabPane):
    CSS_PATH = "tui/projects.tcss"
    
    
    def compose(self) -> ComposeResult:
        
        yield VerticalScroll(Static("Drücke [b]L[/b], um GCP-Projekte zu laden.\n", id="output"), id="output_container")
        yield Vertical(Button("📋 GCP-Projekte laden", id="load_projects"))
        
        # yield Static("Home Tab Content", id="projects_label", classes="header")
        # yield VerticalScroll(
        #     Static("Drücke [b]L[/b], um GCP-Projekte zu laden.\n", id="projects_output"), 
        #     id="projects_output_container"
        # )
        # yield Vertical(
        #     Button("📦 GCP-Projekte laden", id="load_projects")
        # )
        
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
            Static("Drücke [b]C[/b], um die GCloud Console zu Authorisieren !.\n", id="console_output"), 
            id="console_output_container"
        )
        
        yield Vertical(
            Button("Authenticate", id="load_projects")
        )
        
        yield Container(
            Static("Console :", id="console_label", classes="console"),
            Log("#console_output", id="console_output", classes="output"),
            ProgressBar(show_eta=False, show_percentage=True, id="console_progressbar", classes="progressbar"),
            id="console_tab_container"
        )



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
            yield XXXTab("TEST")
            yield SettingsTab("Settings")
            yield ProjectsTab("Projects")
            yield ConsoleTab("Console") 
            yield VMTab("VM-Instanzen")
            yield LogTab("Logs")
        
        yield Footer()




if __name__ == "__main__":
    GCloudConsoleApp().run()
