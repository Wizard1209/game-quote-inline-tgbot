from pathlib import Path
from typing import Any, Optional
from pydantic import Field, ValidationError, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    if Path(".env").exists():
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    else:
        model_config = SettingsConfigDict()

    bot_token: str = Field(validate_default=True)

    # TODO: support optional
    # TODO: validate for webhooks, ignore for polling
    webhook_host: str = Field(validate_default=True)
    webhook_path: str = Field(validate_default=True)

    backend_host: str = Field(validate_default=True)
    backend_port: int = Field(validate_default=True)

    admin_ids: Optional[list[int]] = Field(default=None, validate_default=True)

    @validator("admin_ids", pre=True)
    def split_ids(cls, ids: Any) -> list[int]:
        if not ids:
            return []
        elif isinstance(ids, int):
            return [ids]
        elif isinstance(ids, str):
            return list(map(int, ids.split(",")))
        else:
            raise ValidationError(
                f"admin_ids must be an int or comma separated list of ints, instead of {type(ids)}"
            )

    @property
    def webhook_url(self) -> str:
        return f"https://{self.webhook_host}{self.webhook_path}"
