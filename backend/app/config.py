from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://mabetek:mabetek@localhost:5432/mabetek"
    secret_key: str = Field(min_length=32)
    admin_username: str = "admin"
    admin_password_hash: str
    public_origin: str = "http://localhost:3000"
    secure_cookies: bool = True
    leads_enabled: bool = False
    privacy_version: str = ""
    lead_limit: int = Field(default=5, ge=1)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = True
    smtp_from: str = ""
    notification_to: str = ""

    @model_validator(mode="after")
    def check_collection(self):
        if self.leads_enabled and not self.privacy_version:
            raise ValueError("PRIVACY_VERSION is required when LEADS_ENABLED=true")
        if not self.admin_password_hash.startswith("$argon2"):
            raise ValueError("ADMIN_PASSWORD_HASH must be an Argon2 hash")
        return self
