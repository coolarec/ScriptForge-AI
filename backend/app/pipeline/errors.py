class ConversionError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        stage: str,
        hints: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.stage = stage
        self.hints = hints or []
