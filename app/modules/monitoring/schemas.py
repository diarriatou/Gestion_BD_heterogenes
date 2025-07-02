from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DatabaseType(str, Enum):
    MYSQL = "mysql"
    MONGODB = "mongodb"
    ORACLE = "oracle"

class SeverityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertType(str, Enum):
    HIGH_CPU = "high_cpu_usage"
    HIGH_MEMORY = "high_memory_usage"
    HIGH_CONNECTIONS = "high_connections"
    HIGH_LATENCY = "high_query_latency"
    CONNECTION_ISSUE = "connection_issue"
    STORAGE_CRITICAL = "storage_critical"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SYSTEM_OVERLOAD = "system_overload"

class DatabaseConnectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nom de la connexion")
    host: str = Field(..., min_length=1, max_length=255, description="Adresse IP ou nom d'hôte")
    port: int = Field(..., ge=1, le=65535, description="Port de connexion")
    db_type: DatabaseType = Field(..., description="Type de base de données")
    username: str = Field(..., min_length=1, max_length=100, description="Nom d'utilisateur")
    password: str = Field(..., min_length=0, max_length=255, description="Mot de passe")
    database_name: str = Field(..., min_length=1, max_length=100, description="Nom de la base de données")
    is_active: bool = Field(default=True, description="Statut actif de la connexion")

    @field_validator('host')
    @classmethod
    def validate_host(cls, v):
        if not v or v.strip() == "":
            raise ValueError("L'adresse hôte ne peut pas être vide")
        return v.strip()

    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        if v < 1 or v > 65535:
            raise ValueError("Le port doit être entre 1 et 65535")
        return v

class DatabaseConnectionCreate(DatabaseConnectionBase):
    pass

class DatabaseConnectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    port: Optional[int] = Field(None, ge=1, le=65535)
    db_type: Optional[DatabaseType] = None
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=0, max_length=255)
    database_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None

class DatabaseConnection(DatabaseConnectionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class MetricBase(BaseModel):
    cpu_usage: Optional[float] = Field(None, ge=0, le=100, description="Utilisation CPU en pourcentage")
    memory_usage: Optional[float] = Field(None, ge=0, le=100, description="Utilisation mémoire en pourcentage")
    disk_usage: Optional[float] = Field(None, ge=0, le=100, description="Utilisation disque en pourcentage")
    connections_count: Optional[int] = Field(None, ge=0, description="Nombre de connexions actives")
    query_latency: Optional[float] = Field(None, ge=0, description="Latence des requêtes en secondes")
    active_transactions: Optional[int] = Field(None, ge=0, description="Nombre de transactions actives")

class MetricCreate(MetricBase):
    database_id: int = Field(..., gt=0, description="ID de la base de données")

class Metric(MetricBase):
    id: int
    database_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class AlertBase(BaseModel):
    alert_type: AlertType
    severity: SeverityLevel
    message: str = Field(..., min_length=1, max_length=1000)
    resolved: bool = Field(default=False)

class AlertCreate(AlertBase):
    database_id: int = Field(..., gt=0)

class Alert(AlertBase):
    id: int
    database_id: int
    timestamp: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class MetricsSummary(BaseModel):
    total_databases: int
    active_databases: int
    total_alerts: int
    critical_alerts: int
    warning_alerts: int
    last_collection: Optional[datetime] = None

class DatabaseHealth(BaseModel):
    database_id: int
    database_name: str
    health_score: float = Field(..., ge=0, le=100)
    status: str
    last_metrics: Optional[Metric] = None
    recent_alerts: List[Alert] = []

class AlertRuleBase(BaseModel):
    metric_name: str
    threshold: float
    comparison: str
    severity: str
    enabled: bool = True

class AlertRuleCreate(AlertRuleBase):
    database_id: int

class AlertRule(AlertRuleBase):
    id: int
    database_id: int
    
    model_config = ConfigDict(from_attributes=True)

class MetricsTimeRange(BaseModel):
    database_id: int
    start_time: datetime
    end_time: Optional[datetime] = None