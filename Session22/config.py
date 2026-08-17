from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding= "utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    ALGORITHM = "HS256"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
