from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DatabaseMetricSchema(BaseModel):
    db_type: str = Field(..., example="MongoDB")  # Type de base (MongoDB, MySQL, Oracle…)
    db_name: str = Field(..., example="test_db")  # Nom de la base surveillée
    database_size_mb: float = Field(..., example=150.5)  # Taille totale de la base
    query_per_second: Optional[float] = Field(None, example=25.7)  # Charge de requêtes
    slow_queries: Optional[int] = Field(None, example=3)  # Nombre de requêtes lentes
    cpu_usage: Optional[float] = Field(None, example=35.2)  # Utilisation CPU en %
    memory_usage: Optional[float] = Field(None, example=65.4)  # Utilisation mémoire en %
    disk_usage: Optional[float] = Field(None, example=80.1)  # Utilisation du disque en %
    active_connections: Optional[int] = Field(None, example=120)  # Connexions actives
    uptime: Optional[int] = Field(None, example=86400)  # Temps de disponibilité (en secondes)
    last_updated: datetime = Field(default_factory=datetime.utcnow)  # Horodatage de la mesure

    class Config:
        schema_extra = {
            "example": {
                "db_type": "MongoDB",
                "db_name": "test_db",
                "database_size_mb": 150.5,
                "query_per_second": 25.7,
                "slow_queries": 3,
                "cpu_usage": 35.2,
                "memory_usage": 65.4,
                "disk_usage": 80.1,
                "active_connections": 120,
                "uptime": 86400,
                "last_updated": "2025-02-18T12:00:00"
            }
        }
