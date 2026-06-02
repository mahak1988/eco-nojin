from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    APP_NAME: str = "Econojin"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    class Config:
        env_file = ".env"
settings = Settings()
