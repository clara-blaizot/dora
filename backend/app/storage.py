"""Petit stockage clé → objet dans un fichier JSON.

Suffisant pour commencer ; à remplacer par une base de données (SQLite) quand
il y aura des comptes utilisateurs.
"""

import json
from pathlib import Path


class JsonStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> dict[str, dict]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text())

    def save(self, data: dict[str, dict]) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
