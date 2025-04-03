from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from typing import Optional
import enum

class BackupStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class BackupType(enum.Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class BackupSchedule(Base):
    __tablename__ = "backup_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    database_id = Column(Integer, ForeignKey("database_connections.id"), nullable=False)
    name = Column(String(100), nullable=False)
    backup_type = Column(Enum(BackupType), default=BackupType.FULL)
    frequency = Column(String(50), nullable=False)  # cron expression
    retention_days: Optional[int] = 30
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    database = relationship("DatabaseConnection", back_populates="backup_schedules")
    backups = relationship("Backup", back_populates="schedule")

class Backup(Base):
    __tablename__ = "backups"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("backup_schedules.id"), nullable=True)
    database_id = Column(Integer, ForeignKey("database_connections.id"), nullable=False)
    backup_type = Column(Enum(BackupType), default=BackupType.FULL)
    file_path = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # taille en bytes
    status = Column(Enum(BackupStatus), default=BackupStatus.PENDING)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retention_days = Column(Integer, default=30)
    
    # Relations
    schedule = relationship("BackupSchedule", back_populates="backups")
    database = relationship("DatabaseConnection", back_populates="backups")