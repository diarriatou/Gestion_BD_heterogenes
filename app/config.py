import os
from dotenv import load_dotenv
from typing import Optional

# Chargement des variables d'environnement
load_dotenv()

class Settings:
    # Configuration de la base de données
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "db_management")
    
    # Configuration de l'API
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "your_secret_key_change_in_production")
    API_ALGORITHM: str = "HS256"
    API_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("API_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Configuration du monitoring
    METRICS_COLLECTION_INTERVAL: int = int(os.getenv("METRICS_COLLECTION_INTERVAL", "60"))  # minutes
    MAX_METRICS_HISTORY: int = int(os.getenv("MAX_METRICS_HISTORY", "100"))
    
    # Configuration des seuils d'alerte par défaut
    DEFAULT_CPU_WARNING: float = float(os.getenv("DEFAULT_CPU_WARNING", "70.0"))
    DEFAULT_CPU_CRITICAL: float = float(os.getenv("DEFAULT_CPU_CRITICAL", "90.0"))
    DEFAULT_MEMORY_WARNING: float = float(os.getenv("DEFAULT_MEMORY_WARNING", "75.0"))
    DEFAULT_MEMORY_CRITICAL: float = float(os.getenv("DEFAULT_MEMORY_CRITICAL", "90.0"))
    
    @property
    def DATABASE_URL(self) -> str:
        """Construit l'URL de connexion à la base de données"""
        if self.DB_PASSWORD:
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"mysql+pymysql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Instance globale des paramètres
settings = Settings()

# Pour la compatibilité avec l'ancien code
DATABASE_URL = settings.DATABASE_URL
API_SECRET_KEY = settings.API_SECRET_KEY
API_ALGORITHM = settings.API_ALGORITHM
API_ACCESS_TOKEN_EXPIRE_MINUTES = settings.API_ACCESS_TOKEN_EXPIRE_MINUTES
