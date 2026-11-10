from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # Database individual fields
    DATABASE_HOST: Optional[str] = "localhost"
    DATABASE_PORT: Optional[int] = 5432
    DATABASE_NAME: Optional[str] = "f1_strategyiq"
    DATABASE_USER: Optional[str] = "postgres"
    DATABASE_PASSWORD: Optional[str] = ""
    
    # Optional full connection URL (e.g. Render / Neon / Supabase convention)
    DATABASE_URL_ENV: Optional[str] = None
    
    # Models
    MODEL_DIR: str = "models/v1"
    
    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_ENV:
            url = self.DATABASE_URL_ENV
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url
        return f"postgresql://{self.DATABASE_USER}:{quote_plus(self.DATABASE_PASSWORD or '')}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
