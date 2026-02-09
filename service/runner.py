import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
MAIN = SRC_DIR / "main.py"

def git_pull():
    subprocess.run(
        ["git", "pull"],
        cwd=BASE_DIR,
        check=True,
    )

def run_pipeline():
    subprocess.run(
        [sys.executable, str(MAIN)],
        cwd=SRC_DIR,
        check=True,
    )

if __name__ == "__main__":
    git_pull()
    run_pipeline()
