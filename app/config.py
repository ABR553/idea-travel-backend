import logging

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("ideatravel")


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://ideatravel:ideatravel@db:5432/ideatravel"
    environment: str = "development"
    debug: bool = True
    allowed_origins: str = "http://localhost:3000"
    admin_username: str = "admin"
    admin_password: str = "admin"
    admin_secret: str = "change-me-in-production-very-secret-key"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def _warn_insecure_admin(self) -> "Settings":
        if self.environment != "development" and self.admin_password == "admin":
            logger.warning(
                "ADMIN_PASSWORD is set to default 'admin' in %s environment. "
                "Change it via ADMIN_PASSWORD env var.",
                self.environment,
            )
        return self


settings = Settings()
