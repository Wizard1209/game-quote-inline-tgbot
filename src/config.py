from pathlib import Path
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    if Path(".env").exists():
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    else:
        model_config = SettingsConfigDict()

    bot_token: str = Field(validate_default=True)

    webhook_host: str = Field(validate_default=True)
    webhook_path: str = Field(validate_default=True)

    backend_host: str = Field(validate_default=True)
    backend_port: int = Field(validate_default=True)

    admin_ids: str | list[str] = Field(validate_default=True)

    @validator("admin_ids")
    def split_ids(cls, ids: str) -> list[str]:
        return ids.split(",")

    @property
    def webhook_url(self) -> str:
        return f"https://{self.webhook_host}/{self.webhook_path}"
