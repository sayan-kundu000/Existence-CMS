from typing import Any, List, Optional


class AppException(Exception):
    """Base application exception with standardized code and status."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Optional[List[Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []


class ResourceNotFoundError(AppException):
    def __init__(self, resource_name: str, identifier: Any = None):
        msg = f"{resource_name} not found" if identifier is None else f"{resource_name} with identifier '{identifier}' not found"
        super().__init__(message=msg, code="RESOURCE_NOT_FOUND", status_code=404)


class ValidationFailedError(AppException):
    def __init__(self, message: str = "The supplied data is invalid.", details: Optional[List[Any]] = None):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422, details=details)


class AuthenticationFailedError(AppException):
    def __init__(self, message: str = "Invalid or expired authentication credentials."):
        super().__init__(message=message, code="AUTHENTICATION_FAILED", status_code=401)


class PermissionDeniedError(AppException):
    def __init__(self, message: str = "Administrative privileges required to perform this action."):
        super().__init__(message=message, code="PERMISSION_DENIED", status_code=403)


class PinRequiredError(AppException):
    def __init__(self, message: str = "Security PIN authorization required. Provide header 'X-Action-PIN'."):
        super().__init__(message=message, code="PIN_REQUIRED", status_code=403)


class PinInvalidError(AppException):
    def __init__(self, attempts_remaining: int):
        msg = f"Invalid security PIN. {attempts_remaining} attempt(s) remaining before temporary lockout."
        super().__init__(message=msg, code="PIN_INVALID", status_code=401, details=[{"attempts_remaining": attempts_remaining}])


class PinLockedError(AppException):
    def __init__(self, minutes_remaining: int):
        msg = f"PIN is temporarily locked due to excessive failed attempts. Please retry in {max(1, minutes_remaining)} minute(s)."
        super().__init__(message=msg, code="PIN_LOCKED", status_code=423, details=[{"minutes_remaining": minutes_remaining}])


class ConflictError(AppException):
    def __init__(self, message: str = "A resource with the specified identifier already exists."):
        super().__init__(message=message, code="RESOURCE_CONFLICT", status_code=409)


class InvalidStateTransitionError(AppException):
    def __init__(self, message: str = "Invalid assessment or session state transition."):
        super().__init__(message=message, code="INVALID_STATE_TRANSITION", status_code=400)


class DatabaseConstraintError(AppException):
    def __init__(self, message: str = "Database constraint violation occurred."):
        super().__init__(message=message, code="DATABASE_CONSTRAINT_VIOLATION", status_code=409)


class BusinessRuleError(AppException):
    def __init__(self, message: str = "A business rule constraint was violated.", details: Optional[List[Any]] = None):
        super().__init__(message=message, code="BUSINESS_RULE_ERROR", status_code=400, details=details)


class RateLimitExceededError(AppException):
    def __init__(self, retry_after_seconds: int = 60, message: Optional[str] = None):
        msg = message or f"Too many requests. Please wait {retry_after_seconds} seconds before retrying."
        super().__init__(
            message=msg,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=[{"retry_after": retry_after_seconds}]
        )
        self.retry_after = retry_after_seconds

