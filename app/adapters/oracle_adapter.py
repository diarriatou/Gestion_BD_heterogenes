import cx_Oracle
import subprocess
import os
from .base import DatabaseAdapter

class OracleAdapter(DatabaseAdapter):
    """Adaptateur pour les bases de données Oracle."""
    def __init__(self, host, port, user, password, service_name):
        dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        self.config = {
            'user': user,
            'password': password,
            'dsn': dsn
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = cx_Oracle.connect(**self.config)
            return True
        except cx_Oracle.DatabaseError as e:
            print(f"Erreur de connexion Oracle: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_users(self):
        """Récupère la liste des utilisateurs Oracle."""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT username FROM all_users")
                users = cursor.fetchall()
                return [user[0] for user in users]
        except cx_Oracle.DatabaseError as e:
            print(f"Erreur lors de la récupération des utilisateurs: {e}")
            return []

    def backup(self, destination_path):
        """Sauvegarde la base de données Oracle avec Data Pump."""
        try:
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            cmd = f"expdp {self.config['user']}/{self.config['password']}@{self.config['dsn']} DIRECTORY=DATA_PUMP_DIR DUMPFILE={destination_path}"
            process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE, check=True)

            return {'status': 'success', 'path': destination_path}
        except subprocess.SubprocessError as e:
            return {'status': 'error', 'message': str(e)}

    def restore(self, backup_path):
        """Restaure la base de données Oracle avec Data Pump."""
        try:
            if not os.path.exists(backup_path):
                return {'status': 'error', 'message': f"Le fichier {backup_path} n'existe pas"}

            cmd = f"impdp {self.config['user']}/{self.config['password']}@{self.config['dsn']} DIRECTORY=DATA_PUMP_DIR DUMPFILE={backup_path}"
            process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE, check=True)

            return {'status': 'success', 'restored_from': backup_path}
        except subprocess.SubprocessError as e:
            return {'status': 'error', 'message': str(e)}

    def create_user(self, username, password):
        """Crée un nouvel utilisateur Oracle."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"CREATE USER {username} IDENTIFIED BY {password}")
                cursor.execute(f"GRANT CONNECT, RESOURCE TO {username}")
                self.connection.commit()
                return {'status': 'success', 'message': f'Utilisateur {username} créé avec succès'}
        except cx_Oracle.DatabaseError as e:
            return {'status': 'error', 'message': str(e)}

    def delete_user(self, username):
        """Supprime un utilisateur Oracle."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DROP USER {username} CASCADE")
                self.connection.commit()
                return {'status': 'success', 'message': f'Utilisateur {username} supprimé avec succès'}
        except cx_Oracle.DatabaseError as e:
            return {'status': 'error', 'message': str(e)}

    def get_metrics(self):
        """Récupère les métriques de la base de données."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM all_users")
                user_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM v$session WHERE status = 'ACTIVE'")
                active_sessions = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(bytes)/1024/1024 AS size_mb FROM dba_data_files")
                db_size = cursor.fetchone()[0]
                
                return {
                    'status': 'success',
                    'user_count': user_count,
                    'active_sessions': active_sessions,
                    'database_size_mb': db_size
                }
        except cx_Oracle.DatabaseError as e:
            return {'status': 'error', 'message': str(e)}