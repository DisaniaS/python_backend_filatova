from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = '127.0.0.1'
    port: int = 8900

class ApiPrefix(BaseModel):
    prefix: str = '/api'

class DBSettings(BaseSettings):
    username: str = "username"
    password: str = "password"
    database: str = "database"
    host: str = "localhost"
    port: int = 5432

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive=False,
        env_nested_delimiter='_',
        env_prefix = "APP_",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DBSettings = DBSettings()

settings = Settings()