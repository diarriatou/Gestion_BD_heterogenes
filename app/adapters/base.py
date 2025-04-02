from abc import ABC, abstractmethod
from datetime import datetime
import os
import shutil

class DatabaseAdapter:
    """Interface commune pour tous les adaptateurs de bases de données."""
    
    def connect(self):
        """Établit la connexion à la base de données."""
        raise NotImplementedError
    
    def disconnect(self):
        """Ferme la connexion à la base de données."""
        raise NotImplementedError
    
    def get_users(self):
        """Récupère la liste des utilisateurs de la base de données."""
        raise NotImplementedError
    
    def create_user(self, username, password, roles=None):
        """Crée un nouvel utilisateur dans la base de données."""
        raise NotImplementedError
    
    def delete_user(self, username):
        """Supprime un utilisateur de la base de données."""
        raise NotImplementedError
    
    def get_performance_metrics(self):
        """Récupère les métriques de performance de la base de données."""
        raise NotImplementedError
    
    def __init__(self, connection_params, backup_dir):
            self.connection_params = connection_params
            self.backup_dir = backup_dir
        
    # Créer le répertoire de sauvegarde s'il n'existe pas
            os.makedirs(backup_dir, exist_ok=True)
    
    def generate_backup_filename(self, db_name):
        """Génère un nom de fichier basé sur le timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{db_name}_{timestamp}"
    
    @abstractmethod
    def backup(self, backup_type="full"):
        """Effectue une sauvegarde de la base de données"""
        pass
    
    @abstractmethod
    def restore(self, backup_file, target_db=None):
        """Restaure une base de données à partir d'une sauvegarde"""
        pass
    
    @abstractmethod
    def validate_backup(self, backup_file):
        """Valide l'intégrité d'une sauvegarde"""
        pass
    
    def cleanup_old_backups(self, retention_days=30):
        """Supprime les sauvegardes plus anciennes que retention_days"""
        cutoff_time = datetime.now().timestamp() - (retention_days * 86400)
        
        for filename in os.listdir(self.backup_dir):
            file_path = os.path.join(self.backup_dir, filename)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                os.remove(file_path)