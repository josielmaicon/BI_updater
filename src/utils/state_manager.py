import json
from pathlib import Path
import hashlib


STATE_FILE = Path("state/registry.json")


class StateManager:
    def __init__(self):
        STATE_FILE.parent.mkdir(exist_ok=True)
        if not STATE_FILE.exists():
            STATE_FILE.write_text("{}")

        self.state = json.loads(STATE_FILE.read_text())

    def _hash_file(self, file_path: str) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def is_new(self, tipo: str, file_path: str) -> bool:
        file_hash = self._hash_file(file_path)
        last_hash = self.state.get(tipo, {}).get("hash")

        return file_hash != last_hash

    def update(self, tipo: str, file_path: str):
        self.state[tipo] = {
            "hash": self._hash_file(file_path)
        }
        STATE_FILE.write_text(
            json.dumps(self.state, indent=2)
        )
