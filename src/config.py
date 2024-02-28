from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

	bot_token: str = Field(validate_default=True)

	webhook_host: str = Field(validate_default=True)
	webhook_path: str = Field(validate_default=True)

	backend_host: str = Field(validate_default=True)
	backend_port: int = Field(validate_default=True)

	@property
	def webhook_url(self) -> str:
		return f"{self.webhook_host}/{self.webhook_path}"
