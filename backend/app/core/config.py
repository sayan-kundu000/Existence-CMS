import os
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    # Application identity and metadata
    APP_NAME: str = os.getenv("APP_NAME", os.getenv("PROJECT_NAME", "Existence"))
    APP_ENV: str = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development"))
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Aliases for backwards compatibility
    @property
    def PROJECT_NAME(self) -> str:
        return self.APP_NAME
        
    @property
    def ENVIRONMENT(self) -> str:
        return self.APP_ENV

    # Security & Tokens
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        os.getenv("SECRET_KEY", "existence_development_secret_key_change_in_production_32bytes_min")
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    @property
    def SECRET_KEY(self) -> str:
        return self.JWT_SECRET_KEY

    @property
    def ALGORITHM(self) -> str:
        return self.JWT_ALGORITHM

    # Database configuration & Render/PostgreSQL connection pooling
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))

    @property
    def DATABASE_URL(self) -> str:
        # Dynamic property to respect runtime overrides (e.g. tests, migrations)
        raw_url = os.getenv("DATABASE_URL", "sqlite:///./existence.db")
        if raw_url.startswith("postgres://"):
            return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
        if raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+psycopg://"):
            return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return raw_url

    # CORS & Network Origins
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,https://*.vercel.app,https://*.onrender.com"
        ).split(",") if origin.strip()
    ]

    # PIN security configuration
    PIN_MAX_FAILED_ATTEMPTS: int = int(os.getenv("PIN_MAX_FAILED_ATTEMPTS", "5"))
    PIN_LOCKOUT_MINUTES: int = int(os.getenv("PIN_LOCKOUT_MINUTES", "15"))
    PIN_SESSION_EXPIRE_MINUTES: int = int(os.getenv("PIN_SESSION_EXPIRE_MINUTES", "15"))

    # Password policy configuration
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    PASSWORD_MAX_LENGTH: int = int(os.getenv("PASSWORD_MAX_LENGTH", "128"))

    # Rate limiting configuration (brute force and abuse prevention)
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() in ("true", "1", "yes")
    RATE_LIMIT_LOGIN_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_LOGIN_PER_MINUTE", "10"))
    RATE_LIMIT_PIN_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PIN_PER_MINUTE", "10"))
    RATE_LIMIT_GENERAL_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_GENERAL_PER_MINUTE", "120"))

    # Security headers configuration
    SECURITY_HEADERS_ENABLED: bool = os.getenv("SECURITY_HEADERS_ENABLED", "True").lower() in ("true", "1", "yes")

    def validate_production_config(self) -> None:
        """
        Validate critical configuration constraints for production deployments (Section 32).
        Fails fast if production is configured with insecure defaults or missing critical secrets.
        """
        if self.ENVIRONMENT == "production":
            insecure_defaults = [
                "existence_development_secret_key_change_in_production_32bytes_min",
                "existence_production_secret_key_change_me_before_deploying_min_32_chars",
                "secret",
                "changeme",
            ]
            if self.JWT_SECRET_KEY in insecure_defaults or len(self.JWT_SECRET_KEY) < 32:
                raise RuntimeError(
                    "FATAL CONFIGURATION ERROR: In production, JWT_SECRET_KEY must be a cryptographically "
                    "secure string of at least 32 characters, not an insecure default."
                )


settings = Settings()

