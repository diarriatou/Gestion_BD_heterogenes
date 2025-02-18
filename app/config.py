import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "db_management")

# Gestion du mot de passe vide
if DB_PASSWORD:
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"mysql+pymysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuration de l'API
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "your_secret_key")
API_ALGORITHM = "HS256"
API_ACCESS_TOKEN_EXPIRE_MINUTES = 30
