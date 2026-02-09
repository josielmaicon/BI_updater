import requests
from pathlib import Path

from core.step_result import StepResult


def baixar_arquivo(download_url: str, temp_dir: Path) -> StepResult:
    try:
        response = requests.get(download_url, stream=True, timeout=120)
        response.raise_for_status()

    except requests.RequestException as e:
        return StepResult(
            success=False,
            message=f"Erro ao baixar arquivo: {str(e)}"
        )

    filename = download_url.split("/")[-1].split("?")[0]
    file_path = temp_dir / filename

    try:
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    except IOError as e:
        return StepResult(
            success=False,
            message=f"Erro ao salvar arquivo: {str(e)}"
        )

    return StepResult(
        success=True,
        message="Arquivo baixado com sucesso",
        data={
            "file_path": str(file_path)
        }
    )
