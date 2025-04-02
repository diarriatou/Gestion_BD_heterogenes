from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class DatabaseConnection(Base):
    __tablename__ = "database_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    db_type = Column(String(50), nullable=False)  # MySQL, MongoDB, Oracle
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    metrics = relationship("Metric", back_populates="database")
    alerts = relationship("Alert", back_populates="database")

    
    backup_schedules = relationship("BackupSchedule", back_populates="database")
    backups = relationship("Backup", back_populates="database")

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    database_id = Column(Integer, ForeignKey("database_connections.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    disk_usage = Column(Float, nullable=True)
    connections_count = Column(Integer, nullable=True)
    query_latency = Column(Float, nullable=True)
    active_transactions = Column(Integer, nullable=True)
    
    database = relationship("DatabaseConnection", back_populates="metrics")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    database_id = Column(Integer, ForeignKey("database_connections.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    alert_type = Column(String(50), nullable=False)  # CPU, Memory, Disk, Connections, Latency
    severity = Column(String(20), nullable=False)  # Low, Medium, High, Critical
    message = Column(Text, nullable=False)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    database = relationship("DatabaseConnection", back_populates="alerts")

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    database_id = Column(Integer, ForeignKey("database_connections.id"))
    metric_name = Column(String(50), nullable=False)
    threshold = Column(Float, nullable=False)
    comparison = Column(String(10), nullable=False)  # >, <, >=, <=, ==
    severity = Column(String(20), nullable=False)
    enabled = Column(Boolean, default=True)