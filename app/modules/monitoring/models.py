from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DatabaseMetric(BaseModel):
    db_type: str  
    db_name: str  # Nom de la base surveillée
    database_size_mb: float  # Taille totale de la base
    query_per_second: Optional[float] = None  # Charge de requêtes
    slow_queries: Optional[int] = None  # Nombre de requêtes lentes
    cpu_usage: Optional[float] = None  # Utilisation CPU en %
    memory_usage: Optional[float] = None  # Utilisation mémoire en %
    disk_usage: Optional[float] = None  # Utilisation du disque en %
    active_connections: Optional[int] = None  # Connexions actives
    uptime: Optional[int] = None  # Temps de disponibilité (en secondes)
    last_updated: datetime = datetime.utcnow()  # Horodatage de la mesure
