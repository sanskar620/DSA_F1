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
            if self.DATABASE_URL.startswith("postgres://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        else:
            pwd = quote_plus(self.DATABASE_PASSWORD or "")
            self.DATABASE_URL = f"postgresql://{self.DATABASE_USER}:{pwd}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        return self

settings = Settings()
