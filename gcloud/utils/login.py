import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ⚠️ Erlaube unsichere HTTP-Redirects (nur für lokale Entwicklung!)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# 🔒 Google Cloud Scopes (z. B. vollständiger Zugriff)
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

def main():
    creds = None

    # 📦 Bereits gespeicherte Token laden
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # 🔄 Wenn keine gültigen Token vorhanden sind: Interaktives Login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔁 Token abgelaufen. Versuche zu aktualisieren ...")
            creds.refresh(Request())
        else:
            print("🌐 Öffne Browser für Login ...")
            flow = InstalledAppFlow.from_client_secrets_file(
                "keys/creds.json", SCOPES
            )
            creds = flow.run_local_server(port=8080)

        # 💾 Speichere neuen Token
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    print("✅ Login erfolgreich!")
    print("🔑 Zugriffstoken:", creds.token)

if __name__ == "__main__":
    main()
