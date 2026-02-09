from pathlib import Path
from core.step_result import StepResult
from config.mappings import FILE_CLASSIFICATION_RULES
from utils.logger import logger


def classificar_arquivos(file_path: str) -> StepResult:
    path = Path(file_path)
    filename = path.name

    logger.debug(f"Classificando arquivo: {filename}")

    for rule in FILE_CLASSIFICATION_RULES:
        logger.debug(f"Testando regra: {rule['match']}")
        if rule["match"] in filename:
            logger.info(f"Arquivo classificado como {rule['tipo']}")
            return StepResult(
                success=True,
                message="Arquivo classificado com sucesso",
                data={
                    "tipo": rule["tipo"],
                    "sharepoint_path": rule["sharepoint_path"],
                    "powerbi_dataset": rule["powerbi_dataset"]
                }
            )

    return StepResult(
        success=False,
        message=f"Arquivo não reconhecido: {filename}"
    )
