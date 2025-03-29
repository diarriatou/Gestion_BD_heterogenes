from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.modules.backups import schemas, service
from app.modules.backups.models import BackupType, BackupStatus, Backup
from app.modules.backups.scheduler import BackupSchedule
from app.modules.monitoring.models import DatabaseConnection

router = APIRouter(
    prefix="/sauvegarde",
    tags=["Sauvegarde"]
)

@router.post("/backups", response_model=schemas.BackupResponse)
async def create_backup(
    backup: schemas.BackupCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Lance une sauvegarde en arriere plan"""
    db_backup = service.create_backup(db, backup)
    if not db_backup:
        raise HTTPException(status_code=404, detail="Database not found")
    
    #Verifie si la base existe
    database = db.query(DatabaseConnection).filter(DatabaseConnection.id == backup.database_id).first()
    if not database:
        raise HTTPException(status_code=404, detail="Database not found")
    
 
# Créer l'entrée de sauvegarde
    db_backup = Backup(
        database_id=backup.database_id,
        backup_type=backup.backup_type,
        status="running",
        started_at=datetime.now(),
        retention_days=backup.retention_days or 30
    )
    db.add(db_backup)
    db.commit()
    db.refresh(db_backup)
    
    # Lancer la sauvegarde en arrière-plan
    background_tasks.add_task(service.execute_backup, db_backup.id)
    
    return db_backup
@router.get("/backups", response_model=List[schemas.BackupResponse])
async def get_backups(
    database_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupère la liste des sauvegardes"""
    query = db.query(Backup)
    
    if database_id:
        query = query.filter(Backup.database_id == database_id)
    
    if status:
        query = query.filter(Backup.status == status)
    
    backups = query.order_by(Backup.created_at.desc()).limit(limit).all()
    return backups

@router.post("/backups/{backup_id}/restore", response_model=schemas.RestoreResponse)
async def restore_backup(
    backup_id: int,
    restore_data: schemas.RestoreCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Restaure une base de données à partir d'une sauvegarde"""
    try:
        background_tasks.add_task(
            service.restore_backup, 
            db, 
            backup_id, 
            restore_data.target_database_id
        )
        return {
            "message": "Restauration lancée en arrière-plan",
            "status": "RUNNING"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedules", response_model=schemas.BackupScheduleResponse)
async def create_backup_schedule(
    schedule: schemas.BackupScheduleCreate,
    db: Session = Depends(get_db)
):
    """Crée un planning de sauvegarde automatique"""
    db_schedule = BackupSchedule(
        database_id=schedule.database_id,
        name=schedule.name,
        backup_type=schedule.backup_type,
        frequency=schedule.frequency,
        retention_days=schedule.retention_days,
        is_active=schedule.is_active
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.get("/schedules", response_model=List[schemas.BackupScheduleResponse])
async def get_backup_schedules(
    database_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des plannings de sauvegarde"""
    query = db.query(BackupSchedule)
    
    if database_id:
        query = query.filter(BackupSchedule.database_id == database_id)
    
    schedules = query.all()
    return schedules