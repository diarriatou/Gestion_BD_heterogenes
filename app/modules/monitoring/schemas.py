from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DatabaseConnectionBase(BaseModel):
    name: str
    host: str
    port: int
    db_type: str  # MySQL, MongoDB, Oracle
    username: str
    password: str

class DatabaseConnectionCreate(DatabaseConnectionBase):
    pass

class DatabaseConnectionResponse(DatabaseConnectionBase):
    id: int
    
    class Config:
        from_attributes = True
class MetricBase(BaseModel):
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    connections_count: Optional[int] = None
    query_latency: Optional[float] = None
    active_transactions: Optional[int] = None

class MetricCreate(MetricBase):
    database_id: int

class MetricResponse(MetricBase):
    id: int
    database_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    alert_type: str
    severity: str
    message: str

class AlertCreate(AlertBase):
    database_id: int

class AlertResponse(AlertBase):
    id: int
    database_id: int
    timestamp: datetime
    resolved: bool
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AlertRuleBase(BaseModel):
    metric_name: str
    threshold: float
    comparison: str
    severity: str
    enabled: bool = True

class AlertRuleCreate(AlertRuleBase):
    database_id: int

class AlertRuleResponse(AlertRuleBase):
    id: int
    database_id: int
    
    class Config:
        from_attributes = True

class MetricsTimeRange(BaseModel):
    database_id: int
    start_time: datetime
    end_time: Optional[datetime] = None