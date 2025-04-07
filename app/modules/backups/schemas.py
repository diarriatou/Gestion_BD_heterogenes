
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BackupBase(BaseModel):
    database_id: int
    backup_type: str = "full"
    retention_days: Optional[int] = 30
class BackupCreate(BackupBase):
    pass

class BackupResponse(BaseModel):
    id: int
    database_id: int
    backup_type: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        orm_mode = True

class RestoreBase(BaseModel):
    backup_id: int
    target_database_id: Optional[int] = None
    point_in_time: Optional[datetime] = None

class RestoreCreate(RestoreBase):
    pass

class RestoreResponse(BaseModel):
    message: str
    status: str

class BackupScheduleResponse(BaseModel):
    id: int
    database_id: int
    name: str
    backup_type: str
    frequency: str
    retention_days: int
    is_active: bool
    
    class Config:
        orm_mode = True

class BackupScheduleCreate(BaseModel):
    database_id: int
    name: str
    backup_type: str = "full"
    frequency: str  # cron expression
    retention_days: int = 30
    is_active: bool = True
