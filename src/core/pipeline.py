import time
from core.step_result import StepResult
from utils.logger import logger


class Pipeline:
    def __init__(self):
        self.results = []

    def run_step(self, step_func, *args, critical=True, **kwargs):
        step_name = step_func.__name__
        logger.info(f"→ Iniciando step: {step_name}")
        logger.debug(f"   Args: {args} | Kwargs: {kwargs}")

        start = time.time()

        try:
            result = step_func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"✕ Exceção no step {step_name}")
            result = StepResult(
                success=False,
                message=f"Exceção não tratada: {str(e)}"
            )

        elapsed = round(time.time() - start, 2)

        logger.info(
            f"{'✓' if result.success else '✕'} "
            f"Step {step_name} finalizado em {elapsed}s — {result.message}"
        )

        if result.data:
            logger.debug(f"   Data retornada: {result.data}")

        self.results.append(result)

        if critical and not result.success:
            raise RuntimeError(result.message)

        return result

    def summary(self):
        success = all(r.success for r in self.results)
        return success, self.results
