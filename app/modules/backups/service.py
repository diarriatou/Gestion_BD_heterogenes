
from datetime import datetime, timedelta
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.modules.monitoring.models import DatabaseConnection
from app.modules.backups.models import Backup
import logging

logger = logging.getLogger(__name__)

BACKUP_ROOT = os.environ.get("BACKUP_DIR", "./backups")

def create_backup(db, backup_data):
    """Crée une entrée de sauvegarde et lance l'exécution"""
    # Créer l'entrée de sauvegarde
    db_backup = Backup(
        database_id=backup_data.database_id,
        backup_type=backup_data.backup_type,
        status="running",
        started_at=datetime.now(),
        retention_days=backup_data.retention_days or 30
    )
    db.add(db_backup)
    db.commit()
    db.refresh(db_backup)
    
    # Lancer l'exécution directement ou en tâche de fond
    # (la partie tâche de fond sera gérée par le routeur)
    
    return db_backup

def get_adapter_for_database(db_id):
    """Obtient l'adaptateur correct pour une base de données"""
    db = SessionLocal()
    try:
        database = db.query(DatabaseConnection).filter(DatabaseConnection.id == db_id).first()
        if not database:
            raise ValueError(f"Base de données non trouvée: {db_id}")
        
        if database.db_type.lower() == "mysql":
            from app.adapters.mysql_adapter import MySQLAdapter
            return MySQLAdapter(
                host=database.host,
                port=database.port,
                user=database.username,
                password=database.password,
                database=database.database_name
            )
        elif database.db_type.lower() == "oracle":
            from app.adapters.oracle_adapter import OracleAdapter
            return OracleAdapter(
                host=database.host,
                port=database.port,
                user=database.username,
                password=database.password,
                service_name=database.database_name
            )
        elif database.db_type.lower() == "mongodb":
            from app.adapters.mongo_adapter import MongoDBAdapter
            return MongoDBAdapter(
                host=database.host,
                port=database.port,
                user=database.username,
                password=database.password,
                database=database.database_name
            )
        else:
            raise ValueError(f"Type de base de données non supporté: {database.db_type}")
    finally:
        db.close()

def execute_backup(backup_id):
    """Exécute une sauvegarde"""
    db = SessionLocal()
    try:
        backup = db.query(Backup).filter(Backup.id == backup_id).first()
        if not backup:
            logger.error(f"Sauvegarde non trouvée: {backup_id}")
            return
        
        adapter = get_adapter_for_database(backup.database_id)
        
        # Obtenir les informations de la base
        database = db.query(DatabaseConnection).filter(DatabaseConnection.id == backup.database_id).first()
        
        # Créer le répertoire spécifique au type de base
        db_type_dir = os.path.join(BACKUP_ROOT, database.db_type.lower())
        os.makedirs(db_type_dir, exist_ok=True)
        
        # Générer le nom de fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(
            db_type_dir, 
            f"{database.name}_{timestamp}_{backup.backup_type}"
        )
        
        logger.info(f"Démarrage de la sauvegarde {backup_id} pour {database.name}")
        result = adapter.backup(backup_path, backup.backup_type)
        
        # Mettre à jour l'entrée de sauvegarde
        backup.file_path = result.get('path')
        backup.file_size = result.get('size', 0)
        backup.status = "completed" if result.get('status') == 'success' else "failed"
        backup.error_message = result.get('message')
        backup.completed_at = datetime.now()
        
        db.commit()
        
        # Nettoyer les anciennes sauvegardes
        cleanup_old_backups(backup.database_id, backup.retention_days)
        
        logger.info(f"Sauvegarde {backup_id} terminée avec statut: {backup.status}")
    except Exception as e:
        logger.error(f"Erreur pendant la sauvegarde {backup_id}: {str(e)}")
        if backup:
            backup.status = "failed"
            backup.error_message = str(e)
            backup.completed_at = datetime.now()
            db.commit()
    finally:
        db.close()

def cleanup_old_backups(database_id, retention_days=30):
    """Supprime les sauvegardes plus anciennes que retention_days"""
    db = SessionLocal()
    try:
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Trouver les sauvegardes expirées
        old_backups = db.query(Backup).filter(
            Backup.database_id == database_id,
            Backup.status == "completed",
            Backup.completed_at < cutoff_date
        ).all()
        
        for backup in old_backups:
            try:
                # Supprimer le fichier
                if backup.file_path and os.path.exists(backup.file_path):
                    os.remove(backup.file_path)
                
                # Supprimer l'entrée de la base
                db.delete(backup)
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage de la sauvegarde {backup.id}: {str(e)}")
        
        db.commit()
    finally:
        db.close()