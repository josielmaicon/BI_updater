class StepResult:
    def __init__(self, success: bool, message: str, data=None):
        self.success = success
        self.message = message
        self.data = data or {}

    def __repr__(self):
        status = "SUCCESS" if self.success else "ERROR"
        return f"<StepResult {status}: {self.message}>"
