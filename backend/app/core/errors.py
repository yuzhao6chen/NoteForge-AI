from typing import Any


class AppError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 500,
        code: str = "app_error",
        hint: str = "",
        detail: Any = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.hint = hint
        self.detail = detail


class LLMClientError(AppError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 502,
        code: str = "llm_error",
        hint: str = "",
        detail: Any = None,
    ):
        super().__init__(
            message,
            status_code=status_code,
            code=code,
            hint=hint,
            detail=detail,
        )
