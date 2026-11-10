from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # Direct database connection URL (standard on Render, Neon, Supabase)
    DATABASE_URL: Optional[str] = None

    # Individual database fallback fields
    DATABASE_HOST: Optional[str] = "localhost"
    DATABASE_PORT: Optional[int] = 5432
    DATABASE_NAME: Optional[str] = "f1_strategyiq"
    DATABASE_USER: Optional[str] = "postgres"
    DATABASE_PASSWORD: Optional[str] = ""
    
    # Models directory
    MODEL_DIR: str = "models/v1"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def assemble_db_url(self):
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            self.DATABASE_URL = url
        else:
            pwd = quote_plus(self.DATABASE_PASSWORD or "")
            self.DATABASE_URL = f"postgresql+psycopg2://{self.DATABASE_USER}:{pwd}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        return self

settings = Settings()
