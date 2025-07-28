
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button
from textual.containers import Vertical, VerticalScroll




class GCloudConsoleApp(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        # VerticalScroll für scrollbaren Bereich
        yield VerticalScroll(Static("Drücke [b]L[/b], um GCP-Projekte zu laden.\n", id="output"), id="output_container")
        yield Vertical(Button("📋 GCP-Projekte laden", id="load_projects"))
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load_projects":
            output_widget = self.query_one("#output", Static)
            output_widget.update("🔄 Lade GCP-Projekte ...")
            try:
                from gcloud_api import list_projects
                projects = list_projects()
                output = "\n".join(
                    f"🔹 {p.get('projectId')} ({p.get('name', 'Kein Name')}) - {p.get('lifecycleState', 'Unbekannt')}"
                    for p in projects
                )
                output_widget.update(f"📋 Gefundene Projekte:\n\n{output}")
            except Exception as e:
                output_widget.update(f"❌ Fehler: {e}")

# if __name__ == "__main__":
#     GCloudConsoleApp().run()
