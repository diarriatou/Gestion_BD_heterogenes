import pymysql
import subprocess
import os
from .base import DatabaseAdapter

class MySQLAdapter(DatabaseAdapter):
    """Adaptateur pour les bases de données MySQL."""
    
    # Objectif : stocker la configuration de la base de données et gérer la connexion à MySQL.
    def __init__(self, host, port, user, password, database):
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }
        self.connection = None
    
    def connect(self):
        """Établit la connexion à la base de données MySQL."""
        try:
            
            self.connection = pymysql.connect(**self.config)
            return True
        except pymysql.Error as e:
            print(f"Erreur de connexion à MySQL: {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion à la base de données MySQL."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_users(self):
        """Récupère la liste des utilisateurs MySQL."""

        # verifier si la connexion est établie
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                # execution de la requête
                cursor.execute("SELECT User, Host FROM mysql.user")
                users = cursor.fetchall()
                # retourner les résultats sous forme de liste de dictionnaires
                return [{"username": user[0], "host": user[1]} for user in users]
        except pymysql.Error as e:
            print(f"Erreur lors de la récupération des utilisateurs: {e}")
            return []

    def create_user(self, username, password, roles=None):
        """Crée un nouvel utilisateur MySQL avec les rôles spécifiés."""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                # Création de l'utilisateur
                cursor.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'")
                
                # Attribution des privilèges selon les rôles
                if roles:
                    for role in roles:
                        if role == 'admin':
                            cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{username}'@'%' WITH GRANT OPTION")
                        elif role == 'read_only':
                            cursor.execute(f"GRANT SELECT ON *.* TO '{username}'@'%'")
                        elif role == 'backup_operator':
                            cursor.execute(f"GRANT SELECT, LOCK TABLES, SHOW VIEW ON *.* TO '{username}'@'%'")
                

            # valide les changements
                cursor.execute("FLUSH PRIVILEGES")
                self.connection.commit()
                return True
        except pymysql.Error as e:
            print(f"Erreur lors de la création de l'utilisateur: {e}")
            return False
    
    def delete_user(self, username):
        """Supprime un utilisateur MySQL."""
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DROP USER '{username}'@'%'")
                cursor.execute("FLUSH PRIVILEGES")
                self.connection.commit()
                return True
        except pymysql.Error as e:
            print(f"Erreur lors de la suppression de l'utilisateur: {e}")
            return False
    
    def get_performance_metrics(self):
        """Récupère les métriques de performance MySQL."""
        if not self.connection:
            self.connect()
        
        metrics = {}
        try:
            with self.connection.cursor() as cursor:
                # Métriques de connexions
                cursor.execute("SHOW STATUS LIKE 'Connections'")
                result = cursor.fetchone()
                if result:
                    metrics['total_connections'] = int(result[1])
                
                # Utilisation de la mémoire
                cursor.execute("SHOW STATUS LIKE 'Innodb_buffer_pool_bytes_data'")
                result = cursor.fetchone()
                if result:
                    metrics['buffer_usage_bytes'] = int(result[1])
                
                # Nombre de requêtes
                cursor.execute("SHOW STATUS LIKE 'Queries'")
                result = cursor.fetchone()
                if result:
                    metrics['total_queries'] = int(result[1])
                
                # Temps de fonctionnement
                cursor.execute("SHOW STATUS LIKE 'Uptime'")
                result = cursor.fetchone()
                if result:
                    metrics['uptime_seconds'] = int(result[1])
                
                return metrics
        except pymysql.Error as e:
            print(f"Erreur lors de la récupération des métriques: {e}")
            return metrics
    
    def backup(self, destination_path):
        """Exécute une sauvegarde de la base de données MySQL."""
        try:
            # Création du répertoire de destination si nécessaire
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Construction de la commande mysqldump
            cmd = [
                'mysqldump',
                f'--host={self.config["host"]}',
                f'--port={self.config["port"]}',
                f'--user={self.config["user"]}',
                f'--password={self.config["password"]}',
                '--add-drop-database',
                '--databases', self.config['database']
            ]
            
            # Exécution de la commande et redirection de la sortie vers le fichier
            with open(destination_path, 'w') as f:
                process = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)
            
            return {
                'status': 'success',
                'path': destination_path,
                'database': self.config['database'],
                'size': os.path.getsize(destination_path)
            }
        except (subprocess.SubprocessError, OSError) as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def restore(self, backup_path):
        """Restaure une base de données MySQL à partir d'une sauvegarde."""
        try:
            # Vérification de l'existence du fichier
            if not os.path.exists(backup_path):
                return {'status': 'error', 'message': f"Le fichier de sauvegarde {backup_path} n'existe pas"}
            
            # Construction de la commande mysql
            cmd = [
                'mysql',
                f'--host={self.config["host"]}',
                f'--port={self.config["port"]}',
                f'--user={self.config["user"]}',
                f'--password={self.config["password"]}'
            ]
            
            # Exécution de la commande avec le contenu du fichier en entrée
            with open(backup_path, 'r') as f:
                process = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, check=True)
            
            return {
                'status': 'success',
                'database': self.config['database'],
                'restored_from': backup_path
            }
        except (subprocess.SubprocessError, OSError) as e:
            return {
                'status': 'error',
                'message': str(e)
            }