import logging
import sys
import re
from app.core.config import settings

# Sensitive patterns to scrub
SENSITIVE_PATTERNS = [
    (re.compile(r'("?(?:password|hashed_password|pin|hashed_pin|secret|token|access_token)"?\s*[:=]\s*"?)([^",\s]+)("?)', re.IGNORECASE), r'\1***REDACTED***\3'),
    (re.compile(r'(postgresql(?:\+psycopg)?://[^:]+:)([^@]+)(@)', re.IGNORECASE), r'\1***REDACTED***\3')
]


class SensitiveDataFilter(logging.Filter):
    """Filter that sanitizes credentials, passwords, and tokens from log messages."""
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, replacement in SENSITIVE_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        return True


def setup_logging():
    """Configure system logger with sanitized output and structured formats."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.addFilter(SensitiveDataFilter())

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Avoid adding duplicate handlers if already configured
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]

    # Silence excessively verbose third party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


logger = logging.getLogger("existence")
