from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mein-projektname",  # Wichtig: Der Name deines Pakets auf PyPI
    version="0.1.0",         # Die Version deines Pakets
    author="Dein Name",
    author_email="deine@email.com",
    description="Eine kurze Beschreibung deiner Anwendung",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deinusername/mein-projekt", # Optional: Link zu deinem Repository
    packages=find_packages(), # Findet automatisch alle Pakete im aktuellen Verzeichnis
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", # Ändere dies entsprechend deiner Lizenz
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Mindestversion von Python
    install_requires=[        # Deine Abhängigkeiten
        "requests",
        "click>=7.0",
        # weitere Pakete
    ],
    entry_points={            # Optional: Für ausführbare Skripte (CLI-Anwendungen)
        "console_scripts": [
            "mein-tool=mein_projekt.main:cli_entry_point", # mein-tool ist der Befehl, mein_projekt.main:cli_entry_point ist der Einstiegspunkt
        ],
    },
)
