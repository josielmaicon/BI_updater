import tempfile
import shutil
from pathlib import Path

class TempManager:
    def __init__(self):
        self.base_path = Path(
            tempfile.mkdtemp(prefix="automation_")
        )

    def path(self) -> Path:
        return self.base_path

    def cleanup(self):
        if self.base_path.exists():
            shutil.rmtree(self.base_path)
