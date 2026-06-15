from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Security & Testing
    test_password: str = Field(default="secure_default_password_change_in_production", alias="TEST_PASSWORD")
    test_admin_email: str = Field(default="admin@econojin.com", alias="TEST_ADMIN_EMAIL")
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    
    # Database
    database_url: str = Field(default="postgresql://user:password@localhost:5432/econojin", alias="DATABASE_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True
        extra = "ignore"

settings = Settings()
