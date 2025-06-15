from sqlalchemy.orm import Session
from app.database import get_db

# Fonction pour obtenir la session de base de données
def get_database_session() -> Session:
    return next(get_db())
