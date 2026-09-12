from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hackout26 - P2P Energy Trading API"
    debug: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
