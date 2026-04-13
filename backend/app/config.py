"""
Clarion — Application Configuration
Loaded from environment variables with validation at startup.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All application settings. Validated at startup."""

    # ─── Database ───
    db_host: str = Field("clarion-db", alias="CLARION_DB_HOST")
    db_port: int = Field(5432, alias="CLARION_DB_PORT")
    db_name: str = Field("clarion", alias="CLARION_DB_NAME")
    db_user: str = Field("clarion", alias="CLARION_DB_USER")
    db_password: str = Field(..., alias="CLARION_DB_PASSWORD")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def database_url_sync(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # ─── Redis ───
    redis_url: str = Field("redis://clarion-redis:6379/0", alias="CLARION_REDIS_URL")

    # ─── JWT ───
    jwt_secret: str = Field(..., alias="CLARION_JWT_SECRET")
    jwt_access_token_expire_minutes: int = Field(15, alias="CLARION_JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(7, alias="CLARION_JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    @property
    def jwt_expire_minutes(self) -> int:
        return self.jwt_access_token_expire_minutes

    @property
    def jwt_refresh_days(self) -> int:
        return self.jwt_refresh_token_expire_days

    # ─── Encryption ───
    master_key_ref: str = Field("clarion-master", alias="CLARION_MASTER_KEY_REF")

    # ─── Ollama ───
    ollama_url: str = Field("http://clarion-ollama:11434", alias="CLARION_OLLAMA_URL")
    default_local_model: str = Field("gemma2", alias="CLARION_DEFAULT_LOCAL_MODEL")

    # ─── External AI ───
    claude_api_key: str | None = Field(None, alias="CLARION_CLAUDE_API_KEY")
    openai_api_key: str | None = Field(None, alias="CLARION_OPENAI_API_KEY")

    # ─── Application ───
    log_level: str = Field("INFO", alias="CLARION_LOG_LEVEL")
    cors_origins: str = Field("https://localhost", alias="CLARION_CORS_ORIGINS")
    frontend_url: str = Field("https://localhost", alias="CLARION_FRONTEND_URL")
    environment: str = Field("development", alias="CLARION_ENVIRONMENT")

    # ─── Email ───
    smtp_host: str | None = Field(None, alias="CLARION_SMTP_HOST")
    smtp_port: int = Field(587, alias="CLARION_SMTP_PORT")
    smtp_user: str | None = Field(None, alias="CLARION_SMTP_USER")
    smtp_password: str | None = Field(None, alias="CLARION_SMTP_PASSWORD")
    smtp_from: str | None = Field(None, alias="CLARION_SMTP_FROM")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton — import this everywhere
settings = Settings()
