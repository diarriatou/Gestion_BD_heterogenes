# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.database import SessionLocal
from app.modules.backups.models import BackupSchedule, BackupType, BackupStatus
from app.modules.backups.service import create_backup, execute_backup

logger = logging.getLogger(__name__)

def run_scheduled_backup(schedule_id):
    """Exécute une sauvegarde planifiée"""
    db = SessionLocal()
    try:
        # Récupérer le planning de sauvegarde
        schedule = db.query(BackupSchedule).filter(BackupSchedule.id == schedule_id).first()
        if not schedule or not schedule.is_active:
            logger.warning(f"Planning de sauvegarde inactive ou non trouvée: {schedule_id}")
            return
        
        # Exécuter la sauvegarde
        logger.info(f"Démarrage de la sauvegarde planifiée: {schedule.name}")
        backup = create_backup(db, schedule.database_id, schedule.backup_type)
        
        # Mettre à jour le planning avec la dernière sauvegarde
        schedule.last_run = datetime.now()
        db.commit()
        
        logger.info(f"Sauvegarde planifiée terminée: {schedule.name}, statut: {backup.status}")
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la sauvegarde planifiée: {str(e)}")
    finally:
        db.close()

def init_scheduler():
    """Initialise le planificateur de sauvegardes"""
    scheduler = BackgroundScheduler()
    db = SessionLocal()
    
    try:
        # Récupérer tous les plannings de sauvegarde actifs
        schedules = db.query(BackupSchedule).filter(BackupSchedule.is_active == True).all()
        
        for schedule in schedules:
            # Créer un déclencheur cron à partir de l'expression de fréquence
            try:
                trigger = CronTrigger.from_crontab(schedule.frequency)
                
                # Ajouter la tâche au planificateur
                scheduler.add_job(
                    run_scheduled_backup,
                    trigger=trigger,
                    args=[schedule.id],
                    id=f"backup_schedule_{schedule.id}",
                    replace_existing=True
                )
                
                logger.info(f"Planning de sauvegarde configuré: {schedule.name} ({schedule.frequency})")
            except Exception as e:
                logger.error(f"Erreur lors de la configuration du planning {schedule.name}: {str(e)}")
    finally:
        db.close()
    
    # Démarrer le planificateur
    scheduler.start()
    logger.info("Planificateur de sauvegardes démarré")
    
    return scheduler