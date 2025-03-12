import oracledb
import subprocess
import os
from .base import DatabaseAdapter

class OracleAdapter(DatabaseAdapter):
    """Adaptateur pour les bases de données Oracle 19c."""
    
    def __init__(self, host, port, user, password, service_name):
        self.config = {
            'user': user,
            'password': password,
            'dsn': f"{host}:{port}/{service_name}"
        }
        self.connection = None
    
    def connect(self):
        """Établit la connexion à la base de données Oracle."""
        try:
            self.connection = oracledb.connect(**self.config)
            return True
        except oracledb.DatabaseError as e:
            print(f"Erreur de connexion à Oracle: {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion à la base de données Oracle."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_users(self):
        """Récupère la liste des utilisateurs Oracle."""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT username FROM all_users ORDER BY username")
                users = cursor.fetchall()
                return [user[0] for user in users]
        except oracledb.DatabaseError as e:
            print(f"Erreur lors de la récupération des utilisateurs: {e}")
            return []
    
    def create_user(self, username, password, roles=None):
        """Crée un nouvel utilisateur Oracle avec les rôles spécifiés."""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"CREATE USER {username} IDENTIFIED BY {password}")
                
                # Attribution des privilèges
                if roles:
                    for role in roles:
                        if role == 'admin':
                            cursor.execute(f"GRANT DBA TO {username}")
                        elif role == 'read_only':
                            cursor.execute(f"GRANT CONNECT TO {username}")
                        elif role == 'backup_operator':
                            cursor.execute(f"GRANT EXP_FULL_DATABASE TO {username}")
                
                self.connection.commit()
                return True
        except oracledb.DatabaseError as e:
            print(f"Erreur lors de la création de l'utilisateur: {e}")
            return False
    
    def delete_user(self, username):
        """Supprime un utilisateur Oracle."""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DROP USER {username} CASCADE")
                self.connection.commit()
                return True
        except oracledb.DatabaseError as e:
            print(f"Erreur lors de la suppression de l'utilisateur: {e}")
            return False
    
    def get_performance_metrics(self):
        """Récupère les métriques de performance Oracle."""
        if not self.connection:
            self.connect()
        
        metrics = {}
        try:
            with self.connection.cursor() as cursor:
                # Sessions actives
                cursor.execute("SELECT COUNT(*) FROM v$session")
                metrics['active_sessions'] = cursor.fetchone()[0]
                
                # Temps de fonctionnement
                cursor.execute("SELECT sysdate - startup_time FROM v$instance")
                metrics['uptime_days'] = cursor.fetchone()[0]
                
                # Nombre de transactions
                cursor.execute("SELECT value FROM v$sysstat WHERE name = 'user commits'")
                metrics['user_commits'] = cursor.fetchone()[0]
                
                return metrics
        except oracledb.DatabaseError as e:
            print(f"Erreur lors de la récupération des métriques: {e}")
            return metrics
    
    def backup(self, destination_path):
        """Exécute une sauvegarde de la base de données Oracle via expdp."""
        try:
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Commande Data Pump Export (expdp)
            cmd = [
                'expdp',
                f"{self.config['user']}/{self.config['password']}@{self.config['dsn']}",
                'FULL=YES',
                f"DUMPFILE={os.path.basename(destination_path)}",
                f"LOGFILE={os.path.basename(destination_path)}.log",
                f"DIRECTORY=DATA_PUMP_DIR"
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            return {
                'status': 'success',
                'path': destination_path,
                'log': destination_path + ".log"
            }
        except (subprocess.SubprocessError, OSError) as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def restore(self, backup_path):
        """Restaure une base de données Oracle via impdp."""
        try:
            if not os.path.exists(backup_path):
                return {'status': 'error', 'message': f"Le fichier {backup_path} n'existe pas"}
            
            cmd = [
                'impdp',
                f"{self.config['user']}/{self.config['password']}@{self.config['dsn']}",
                'FULL=YES',
                f"DUMPFILE={os.path.basename(backup_path)}",
                f"LOGFILE={os.path.basename(backup_path)}.log",
                f"DIRECTORY=DATA_PUMP_DIR"
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            return {
                'status': 'success',
                'database': self.config['dsn'],
                'restored_from': backup_path
            }
        except (subprocess.SubprocessError, OSError) as e:
            return {
                'status': 'error',
                'message': str(e)
            }
